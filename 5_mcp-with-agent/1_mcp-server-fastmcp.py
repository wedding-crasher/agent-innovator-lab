from mcp.server.fastmcp import FastMCP, Context
import httpx
from bs4 import BeautifulSoup
from typing import List
from dataclasses import dataclass
import urllib.parse
import asyncio
import re
import json

@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str
    position: int

class DuckDuckGo:
    URL = "https://html.duckduckgo.com/html"
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.URL, data={"q": query}, headers=self.HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for i, r in enumerate(soup.select(".result")):
            if i >= max_results:
                break
            a = r.select_one(".result__title a")
            if not a:
                continue
            title = a.text.strip()
            link = a.get("href", "")
            snippet = r.select_one(".result__snippet")
            snippet_text = snippet.text.strip() if snippet else ""
            if link.startswith("//duckduckgo.com/l/?uddg="):
                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
            results.append(SearchResult(title, link, snippet_text, i + 1))
        return results

    def format(self, results: List[SearchResult]) -> str:
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{r.position}. {r.title}\nURL: {r.link}\n{r.snippet}" for r in results
        )

class WebFetcher:
    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        text = " ".join(
            chunk.strip() for line in soup.get_text().splitlines() for chunk in line.split("  ") if chunk.strip()
        )
        return re.sub(r"\s+", " ", text).strip()[:8000]

class JsonFormatter:
    def format_json(self, obj: object) -> str:
        try:
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Failed to convert to JSON: {str(e)}"

mcp = FastMCP("ddg-demo")
ddg = DuckDuckGo()
fetcher = WebFetcher()
formatter = JsonFormatter()

@mcp.tool()
async def search(query: str, ctx: Context, max_results: int = 10) -> str:
    await ctx.info(f"Searching: {query}")
    try:
        results = await ddg.search(query, max_results)
        return ddg.format(results)
    except Exception as e:
        await ctx.error(str(e))
        return "Search failed."

@mcp.tool()
async def fetch_content(url: str, ctx: Context) -> str:
    await ctx.info(f"Fetching: {url}")
    try:
        return await fetcher.fetch(url)
    except Exception as e:
        await ctx.error(str(e))
        return "Failed to fetch content."

if __name__ == "__main__":
    asyncio.run(mcp.run_streamable_http_async())