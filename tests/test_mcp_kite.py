import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def test_kite_mcp():
    print("--- TESTING KITE MCP SERVER DATA FETCHING ---")
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", "https://mcp.kite.trade/mcp"]
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("SUCCESS: Connected to Kite MCP!\n")
                
                # 1. Inspect the get_ltp tool to see what arguments it expects
                tools_response = await session.list_tools()
                ltp_tool = next((t for t in tools_response.tools if t.name == "get_ltp"), None)
                
                if ltp_tool:
                    print(f"-> 'get_ltp' Schema: {json.dumps(ltp_tool.inputSchema, indent=2)}\n")
                    
                    # 2. Execute get_ltp (Latest Trading Price)
                    # Kite standard API usually expects a list of instruments like ["NSE:RELIANCE"]
                    print("-> Executing 'get_ltp' for NSE:RELIANCE and NSE:M&M...")
                    try:
                        ltp_result = await session.call_tool("get_ltp", {"instruments": ["NSE:RELIANCE", "NSE:M&M"]})
                        # Extract the text content from the MCP tool result
                        text_content = next((item.text for item in ltp_result.content if item.type == 'text'), "No text returned")
                        print(f"[LTP RESULT]:\n{text_content}\n")
                    except Exception as e:
                        print(f"Error calling get_ltp: {e}")

                # 3. Execute get_ohlc (Open, High, Low, Close)
                ohlc_tool = next((t for t in tools_response.tools if t.name == "get_ohlc"), None)
                if ohlc_tool:
                    print("-> Executing 'get_ohlc' for NSE:RELIANCE...")
                    try:
                        ohlc_result = await session.call_tool("get_ohlc", {"instruments": ["NSE:RELIANCE"]})
                        text_content = next((item.text for item in ohlc_result.content if item.type == 'text'), "No text returned")
                        print(f"[OHLC RESULT]:\n{text_content}\n")
                    except Exception as e:
                        print(f"Error calling get_ohlc: {e}")
                        
    except Exception as e:
        print(f"\nFAILED to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_kite_mcp())
