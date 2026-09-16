import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def verify_cached_auth():
    print("--- VERIFYING CACHED MCP SESSION ---")
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", "https://mcp.kite.trade/mcp"]
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("Connected to MCP Server. Fetching data without logging in...\n")
                
                try:
                    # Directly ask for data, completely skipping the login tool!
                    ltp_result = await session.call_tool("get_ltp", {"instruments": ["NSE:RELIANCE"]})
                    text_content = next((item.text for item in ltp_result.content if item.type == 'text'), "")
                    
                    if "Please log in" in text_content:
                        print("FAILED: The server did not remember your session. It asked you to log in again.")
                    else:
                        print("SUCCESS! The session is perfectly cached!")
                        print(f"[LTP RESULT]:\n{text_content}\n")
                        
                except Exception as e:
                    print(f"Data fetch failed: {e}")

    except Exception as e:
        print(f"\nFATAL: {e}")

if __name__ == "__main__":
    asyncio.run(verify_cached_auth())
