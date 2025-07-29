import json
import time
from collections import Counter
from typing import Annotated

import anyio
import typer
from fastmcp import Client
from mcp.types import TextContent

from daydream import mcp
from daydream.clilib.client import app as client_app
from daydream.clilib.options import PROFILE_OPTION
from daydream.config import load_config
from daydream.config.utils import get_config_dir
from daydream.knowledge import Graph
from daydream.mcp import Context, build_mcp_server
from daydream.plugins import PluginManager
from daydream.plugins.mixins import KnowledgeGraphMixin
from daydream.telemetry import client as telemetry

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)
tools_app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True
)
app.add_typer(tools_app, name="tools")
app.add_typer(client_app, name="client")


@app.command()
def start(
    profile: str = PROFILE_OPTION,
    disable_sse: bool = typer.Option(
        False, "--disable-sse", help="Disable the SSE transport for the MCP Server"
    ),
    disable_stdio: bool = typer.Option(
        False, "--disable-stdio", help="Disable the stdio transport for the MCP Server"
    ),
) -> None:
    """Start the Daydream MCP Server"""

    async def _start() -> None:
        await telemetry.send_event(
            {
                "command": "start",
                "profile": profile,
                "disable_sse": disable_sse,
                "disable_stdio": disable_stdio,
            }
        )
        await mcp.start(profile, disable_sse, disable_stdio)

    anyio.run(_start)


@app.command()
def build_graph(
    profile: str = PROFILE_OPTION,
) -> None:
    """Build a knowledge graph for your cloud infrastructure"""

    async def _build_graph() -> None:
        print("Building graph...")

        start_time = time.perf_counter()

        graph = Graph()
        config = load_config(profile, create=True)
        output_path = (get_config_dir(profile) / "graph.json").resolve()
        plugin_manager = PluginManager(config)

        async with anyio.create_task_group() as tg:
            for plugin in plugin_manager.get_plugins_with_capability(KnowledgeGraphMixin):
                print(f"Populating graph with the {plugin.name} plugin...")
                tg.start_soon(plugin.populate_graph, graph)

        await graph.infer_edges()

        print(f"Saving graph to {output_path!s}...")
        await graph.save(output_path)

        end_time = time.perf_counter()
        total_time = end_time - start_time
        edge_counts = Counter(
            [edge.properties["relationship_type"] async for edge in graph.iter_edges()]
        )
        node_counts = Counter([node.node_type async for node in graph.iter_nodes()])

        print("=== Summary ===")

        print("Edges:")
        for relationship_type, count in edge_counts.items():
            print(f"  {relationship_type}: {count}")
        print("Nodes:")
        for node_type, count in node_counts.items():
            print(f"  {node_type}: {count}")

        print(f"Graph built in {total_time:.2f} seconds")
        print(f"Graph saved to {output_path!s}")
        print("=== End Summary ===")

        await telemetry.send_event(
            {
                "command": "build_graph",
                "profile": profile,
                "duration_seconds": total_time,
                "node_counts": node_counts,
                "edge_counts": edge_counts,
            }
        )

    anyio.run(_build_graph)


@app.command()
def visualize(
    profile: str = PROFILE_OPTION,
    topology: bool = typer.Option(False, "--topology"),
) -> None:
    """Visualize the knowledge graph topology"""

    async def _visualize() -> None:
        await telemetry.send_event(
            {
                "command": "visualize_graph",
                "profile": profile,
                "topology_only": topology,
            }
        )

        graph = Graph(get_config_dir(profile) / "graph.json")

        if topology:
            graph = await graph.get_topology()

        print(await graph.to_pydot())

    anyio.run(_visualize)


@tools_app.command("list")
def list_tools(
    profile: str = PROFILE_OPTION,
) -> None:
    """List all MCP tools available from enabled plugins."""

    async def _list_tools() -> None:
        config = load_config(profile)
        plugins = PluginManager(config=config)
        context = Context(
            profile=profile,
            config=config,
            plugins=plugins,
            graph=Graph(get_config_dir(profile) / "graph.json"),
        )
        mcp = build_mcp_server(context)

        tools = await mcp.get_tools()
        for key, tool in tools.items():
            cmd = [key]
            for arg, arg_data in tool.parameters["properties"].items():
                arg_type = arg_data.get("type", "unknown")
                if "anyOf" in arg_data:
                    arg_type = "|".join(t["type"] for t in arg_data["anyOf"])
                cmd.append(f"<{arg}:{arg_type}>")
            print(" ".join(cmd))

    anyio.run(_list_tools)


@tools_app.command()
def call(
    tool: str,
    arguments: Annotated[list[str] | None, typer.Argument()] = None,
    profile: str = PROFILE_OPTION,
) -> None:
    """Call an MCP tool from the command line."""

    async def _call_tool() -> None:
        config = load_config(profile)
        plugins = PluginManager(config=config)
        context = Context(
            profile=profile,
            config=config,
            plugins=plugins,
            graph=Graph(get_config_dir(profile) / "graph.json"),
        )
        mcp = build_mcp_server(context)

        tools = await mcp.get_tools()
        if tool not in tools:
            raise typer.Abort(f"Tool {tool} not found")

        tool_def = tools[tool]
        tool_args = {}
        if arguments:
            # Convert a list of arguments into a dict
            for k, v in zip(tool_def.parameters["properties"].keys(), arguments, strict=True):
                # Try decoding as JSON to handle complex arguments (lists, dicts, etc.)
                try:
                    tool_args[k] = json.loads(v)
                except json.JSONDecodeError:
                    tool_args[k] = v

        client = Client(mcp)
        async with client:
            result = await client.call_tool(tool, tool_args)
            try:
                print(next(r.text for r in result if isinstance(r, TextContent)))
            except StopIteration:
                print(f"{tool} returned no printable results")

    anyio.run(_call_tool)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
