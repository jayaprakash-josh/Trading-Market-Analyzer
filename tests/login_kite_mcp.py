import asyncio
import os
import sys
import json
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

load_dotenv()

async def authenticate_and_fetch():
    print("--- KITE MCP AUTHENTICATION ---")
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", "https://mcp.kite.trade/mcp"]
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("Connected to MCP Server!")
                
                # 1. Find the login tool
                tools_response = await session.list_tools()
                login_tool = next((t for t in tools_response.tools if 'login' in t.name.lower()), None)
                
                if login_tool:
                    print(f"Found Login Tool! Expected arguments: {login_tool.input_schema}")
                    
                    # 2. Try to login using the enctoken
                    enctoken = os.getenv("KITE_ENCTOKEN")
                    if not enctoken:
                        print("ERROR: KITE_ENCTOKEN not set in .env")
                        return
                    
                    # Let's dynamically guess the param name based on the schema
                    schema_props = login_tool.input_schema.get('properties', {})
                    param_name = list(schema_props.keys())[0] if schema_props else "token"
                    
                    print(f"Attempting login using param '{param_name}'...")
                    
                    try:
                        login_res = await session.call_tool(login_tool.name, {})
                        text_content = next((item.text for item in login_res.content if item.type == 'text'), "")
                        print(f"\n============================================\n{text_content}\n============================================\n")
                        
                        # Wait for user to actually click the link and authenticate!
                        # We must use asyncio to run input() without blocking the event loop
                        await asyncio.to_thread(input, "ACTION REQUIRED: Click the URL above, log in, and then PRESS ENTER HERE to continue...")
                        
                    except Exception as e:
                        print(f"Login tool failed: {e}")
                        
                # 3. Now try to fetch the data again!
                print("\nAttempting to fetch NSE:RELIANCE after login...")
                try:
                    ltp_result = await session.call_tool("get_ltp", {"instruments": ["NSE:RELIANCE"]})
                    text_content = next((item.text for item in ltp_result.content if item.type == 'text'), "")
                    print(f"[LTP RESULT]:\n{text_content}\n")
                except Exception as e:
                    print(f"Data fetch failed: {e}")

    except Exception as e:
        print(f"\nFATAL: {e}")

if __name__ == "__main__":
    asyncio.run(authenticate_and_fetch())
