import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def explore_kite_data():
    print("--- KITE MCP DATA EXPLORATION ---")
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", "https://mcp.kite.trade/mcp"]
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # 1. Discover ALL Tools
                print("\n[STEP 1]: Discovering ALL 22 Available Tools...")
                tools_response = await session.list_tools()
                for t in tools_response.tools:
                    print(f" - {t.name}: {t.description}")
                    
                # 2. Login Step
                print("\n[STEP 2]: Requesting Login URL...")
                login_tool = next((t for t in tools_response.tools if 'login' in t.name.lower()), None)
                if login_tool:
                    login_res = await session.call_tool("login", {})
                    text_content = next((item.text for item in login_res.content if item.type == 'text'), "")
                    print(f"\n============================================\n{text_content}\n============================================\n")
                    await asyncio.to_thread(input, "ACTION REQUIRED: Click the URL above, log in, and then PRESS ENTER HERE...")
                
                # 3. Check for specific Pre-Market / Options data tools
                quote_tool = next((t for t in tools_response.tools if 'quote' in t.name.lower()), None)
                if quote_tool:
                    print(f"\n[STEP 3]: Found '{quote_tool.name}' tool! Fetching advanced market data (Volume, Depth, OI)...")
                    try:
                        # Assuming the argument is 'instruments' based on get_ltp
                        quote = await session.call_tool(quote_tool.name, {"instruments": ["NSE:RELIANCE"]})
                        print(next((item.text for item in quote.content if item.type == 'text'), ""))
                    except Exception as e:
                        print(f"Quote Error: {e}")
                else:
                    print("\n[STEP 3]: No 'quote' tool found. Falling back to get_ohlc...")
                    try:
                        ohlc = await session.call_tool("get_ohlc", {"instruments": ["NSE:RELIANCE"]})
                        print(next((item.text for item in ohlc.content if item.type == 'text'), ""))
                    except Exception as e:
                        print(f"OHLC Error: {e}")

    except Exception as e:
        print(f"\nFATAL: {e}")

if __name__ == "__main__":
    asyncio.run(explore_kite_data())
