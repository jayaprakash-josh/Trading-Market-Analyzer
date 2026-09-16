import asyncio
import os
import sys
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

load_dotenv()

async def test_mcp_auth():
    print("--- ATTEMPTING MCP CONNECTION WITH ENCTOKEN ---")
    
    # We will pass your enctoken into the subprocess environment variables
    # so that mcp-remote can forward it to the server.
    env = os.environ.copy()
    if not env.get("KITE_ENCTOKEN"):
        print("ERROR: KITE_ENCTOKEN not found in .env")
        return
        
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", "https://mcp.kite.trade/mcp"],
        env=env
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("SUCCESS: Connected to MCP Proxy.\n")
                
                print("Fetching tools (testing connection stability)...")
                await session.list_tools()
                
                print("Requesting live data for NSE:RELIANCE...")
                try:
                    result = await session.call_tool("get_ltp", {"instruments": ["NSE:RELIANCE"]})
                    print(f"Data Received: {result.content}")
                except Exception as e:
                    print(f"Server rejected data request: {e}")
                    
    except Exception as e:
        print(f"\nFATAL CRASH (Server disconnected): {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_auth())
