import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def f():
    server_params = StdioServerParameters(command='npx', args=['-y','mcp-remote','https://mcp.kite.trade/mcp'])
    async with stdio_client(server_params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            t = await s.list_tools()
            for tool in t.tools:
                if 'login' in tool.name.lower() or 'auth' in tool.name.lower():
                    print(f"FOUND AUTH TOOL: {tool.name}")
                    print(tool.input_schema)

if __name__ == "__main__":
    asyncio.run(f())
