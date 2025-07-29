from asyncio import run
from typing import Any

from fastmcp import Client
from rich import print as pr

from .mcp_server import mcp


async def call_resource(resource: str):
    async with Client(mcp) as client:
        result = await client.read_resource(resource)
        pr(f"Resource <{resource}>: {result}")


async def call_tool(tool: str, args: dict[str, Any]):
    async with Client(mcp) as client:
        result = await client.call_tool(tool, args)
        pr(f"Tool <{tool}>: {result}")


run(call_resource("data://torrent_categories"))
run(call_tool("search_torrents", {"query": "berserk", "limit": 3}))
run(call_tool("get_torrent_details", {"torrent_id": 1268760, "with_magnet_link": True}))
run(call_tool("get_magnet_link", {"torrent_id": 1268760}))
