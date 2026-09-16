import asyncio
import sys

async def run_mcp_interactive():
    print("--- STARTING KITE MCP (INTERACTIVE MODE) ---")
    print("This will print the raw logs so you can see the OAuth/Login link.\n")
    
    # Spawn the process directly to capture raw stderr (which contains the login links/logs)
    process = await asyncio.create_subprocess_exec(
        "npx.cmd", "-y", "mcp-remote", "https://mcp.kite.trade/mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    async def read_stderr():
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            # Print the raw logs to the terminal so you can click any authentication links
            sys.stdout.write(f"[MCP LOG]: {line.decode('utf-8')}")
            sys.stdout.flush()

    # Start listening to logs in the background
    asyncio.create_task(read_stderr())
    
    # Wait for a few seconds to let the OAuth logs print
    await asyncio.sleep(10)
    print("\n--- WAITING FOR AUTHENTICATION ---")
    print("If you see an OAuth link above, please click it to authenticate.")
    print("Once authenticated, you can kill this script (Ctrl+C).")
    
    # Keep it alive
    await process.wait()

if __name__ == "__main__":
    try:
        asyncio.run(run_mcp_interactive())
    except KeyboardInterrupt:
        print("\nExiting...")
