import argparse
import html
import logging
from pathlib import Path
import re
from typing import Any

import aiosqlite
import anyio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field
import yaml


class TableMetadata(BaseModel):
    hidden: bool = Field(False, exclude=True)
    columns: dict[str, str] = {}
    model_config = {
        "extra": "allow",
    }


class QueryMetadata(BaseModel):
    sql: str
    model_config = {
        "extra": "allow",
    }


class DatabaseMetadata(BaseModel):
    tables: dict[str, TableMetadata] = {}
    queries: dict[str, QueryMetadata] = {}
    model_config = {
        "extra": "allow",
    }


class RootMetadata(BaseModel):
    databases: dict[str, DatabaseMetadata] = {}
    model_config = {
        "extra": "allow",
    }


async def get_catalog(sqlite_connection: aiosqlite.Connection, metadata: RootMetadata) -> RootMetadata:
    # Copy all metadata except databases
    catalog = RootMetadata(**{key: value for key, value in metadata if key != "databases"})
    # Get the true database names and stems of their filepaths
    cursor = await sqlite_connection.execute("pragma database_list")
    for database_name, database_stem in [
        (database_row[1], Path(database_row[2]).stem) for database_row in await cursor.fetchall()
    ]:
        database_in_metadata = database_stem in metadata.databases
        # Rename from the stem to the true SQLite-internal name (usually "main")
        database = DatabaseMetadata(
            **(
                {key: value for key, value in metadata.databases[database_stem] if key != "tables"}
                if database_in_metadata
                else {}
            )
        )
        # Get the table names
        cursor = await sqlite_connection.execute(f"pragma {database_name}.table_list")
        for table_name in [
            table_row[1] for table_row in await cursor.fetchall() if not table_row[1].startswith("sqlite_")
        ]:
            table_in_metadata = database_in_metadata and table_name in metadata.databases[database_stem].tables
            table = TableMetadata(
                **(
                    {
                        key: value
                        for key, value in metadata.databases[database_stem].tables[table_name]
                        if key != "columns"
                    }
                    if table_in_metadata
                    else {}
                )
            )
            # Omit hidden tables
            if table.hidden:
                continue
            # Get the column names
            cursor = await sqlite_connection.execute(f"pragma {database_name}.table_info({table_name})")
            for column_name in [column_row[1] for column_row in await cursor.fetchall()]:
                column_in_metadata = (
                    table_in_metadata and column_name in metadata.databases[database_stem].tables[table_name].columns
                )
                column_description = (
                    metadata.databases[database_stem].tables[table_name].columns[column_name]
                    if column_in_metadata
                    else ""
                )
                table.columns[column_name] = column_description
            database.tables[table_name] = table
        catalog.databases[database_name] = database
    return catalog


async def execute(sqlite_connection: aiosqlite.Connection, sql: str, parameters: dict[str, str] = {}) -> str:
    cursor = await sqlite_connection.execute(sql, parameters)
    if not cursor.description:
        return "Statement executed successfully"
    header_inner_html = ""
    for column_description in cursor.description:
        header_inner_html += f"<th>{html.escape(column_description[0])}</th>"
    rows_html = f"<tr>{header_inner_html}</tr>"
    for row in await cursor.fetchall():
        row_inner_html = ""
        for value in row:
            row_inner_html += f"<td>{html.escape(str(value))}</td>"
        rows_html += f"<tr>{row_inner_html}</tr>"
    return f"<table>{rows_html}</table>"


async def mcp_sqlite_server(sqlite_connection: aiosqlite.Connection, metadata: RootMetadata = RootMetadata()) -> Server:
    """Create a catalog of databases, tables, and columns that are actually in the connection, enriched with optional metadata."""
    server = Server("mcp-sqlite")

    initial_catalog = await get_catalog(sqlite_connection=sqlite_connection, metadata=metadata)
    canned_queries = {}
    for database in initial_catalog.databases:
        for query_slug, query in initial_catalog.databases[database].queries.items():
            # Extract named parameters from the query SQL
            query_params = re.findall(r":(\w+)", query.sql)
            canned_queries[f"{database}_{query_slug}"] = (query_params, query.sql)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        tools = [
            Tool(
                name="sqlite_get_catalog",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="sqlite_execute",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                        }
                    },
                    "required": ["sql"],
                },
            ),
        ]
        for query_name, (query_params, _) in canned_queries.items():
            tools.append(
                Tool(
                    name=f"sqlite_execute_{query_name}",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            param: {
                                "type": "string",
                            }
                            for param in query_params
                        },
                        "required": query_params,
                    },
                )
            )
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, str]) -> list[TextContent]:
        if name == "sqlite_get_catalog":
            catalog = await get_catalog(sqlite_connection=sqlite_connection, metadata=metadata)
            return [TextContent(type="text", text=catalog.model_dump_json())]
        elif name == "sqlite_execute":
            return [TextContent(type="text", text=await execute(sqlite_connection, arguments["sql"]))]
        elif name.startswith("sqlite_execute_"):
            query_name = name.removeprefix("sqlite_execute_")
            if query_name in canned_queries:
                _, query_sql = canned_queries[query_name]
                return [TextContent(type="text", text=await execute(sqlite_connection, query_sql, arguments))]
        raise ValueError(f"Unknown tool: {name}")

    return server


async def run_server(sqlite_file: str, metadata_yaml_file: str | None = None, write: bool = False):
    if metadata_yaml_file:
        with open(metadata_yaml_file, "r") as metadata_file_descriptor:
            metadata_dict = yaml.safe_load(metadata_file_descriptor.read())
    else:
        metadata_dict = {}
    async with aiosqlite.connect(f"file:{sqlite_file}?mode={'rw' if write else 'ro'}", uri=True) as sqlite_connection:
        server = await mcp_sqlite_server(sqlite_connection=sqlite_connection, metadata=RootMetadata(**metadata_dict))
        options = server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, options)


def main_cli():
    parser = argparse.ArgumentParser(
        prog="mcp-sqlite-server",
        description="CLI command to start an MCP server for interacting with SQLite data.",
    )
    parser.add_argument(
        "sqlite_file",
        help="Path to SQLite file to serve the MCP server for.",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        help="Path to Datasette-compatible metadata JSON file.",
    )
    parser.add_argument(
        "-w",
        "--write",
        help="Set this flag to allow the AI agent to write to the database. By default the database is opened in read-only mode.",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose. Include once for INFO output, twice for DEBUG output.",
        action="count",
        default=0,
    )
    args = parser.parse_args()
    LOGGING_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=LOGGING_LEVELS[min(args.verbose, len(LOGGING_LEVELS) - 1)])  # cap to last level index
    anyio.run(run_server, args.sqlite_file, args.metadata, args.write)


if __name__ == "__main__":
    main_cli()
