import asyncio
from fastmcp import Client

SERVER_URL ="http://127.0.0.1:8000/mcp"
client = Client(SERVER_URL)

async def main():
    try:
        async with client:
            print(" Pinging MCP server...")
            await client.ping()
            print(" MCP server is alive.\n")
            tools = await client.list_tools()
            print(f"Available tools: {tools}")
            # 1. Search Tool
            print("############## Calling 'search' tool...######################")
            result = await client.call_tool("search", {"query": "What is quantum computing?"})
            print("\n Search Result:\n", result)

            # # 2. Fetch Content Tool
            # print("\n############ Calling 'fetch_content' tool...################")
            # test_url = "https://en.wikipedia.org/wiki/Quantum_computing"
            # content_result = await client.call_tool("fetch_content", {"url": test_url})
            # print("\n Fetched Web Content:\n", content_result[:1000], "\n... (truncated)")

    except Exception as e:
        print(" Error during client test:", e)

if __name__ == "__main__":
    asyncio.run(main())
