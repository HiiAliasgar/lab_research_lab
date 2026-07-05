import asyncio
import re
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from app.models import Source

HEADERS = {"User-Agent": "AgentResearchLab/0.1 (educational research tool)"}


def _clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", unescape(value))).strip()


async def search_web(query: str, limit: int) -> list[Source]:
    async with httpx.AsyncClient(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        response = await client.get("https://html.duckduckgo.com/html/", params={"q": query})
        response.raise_for_status()
    blocks = re.findall(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'class="result__snippet"[^>]*>(.*?)</(?:a|div)>',
        response.text,
        re.DOTALL,
    )
    results: list[Source] = []
    for href, title, snippet in blocks[:limit]:
        parsed = urlparse(unescape(href))
        url = unquote(parse_qs(parsed.query).get("uddg", [href])[0])
        results.append(
            Source(
                title=_clean_html(title),
                url=url,
                snippet=_clean_html(snippet),
                source_type="web",
            )
        )
    return results


async def search_openalex(query: str, limit: int) -> list[Source]:
    params = {
        "search": query,
        "per-page": limit,
        "sort": "cited_by_count:desc",
        "select": "id,display_name,publication_year,doi,primary_location,cited_by_count",
    }
    async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
        response = await client.get("https://api.openalex.org/works", params=params)
        response.raise_for_status()
    sources = []
    for work in response.json().get("results", []):
        location = work.get("primary_location") or {}
        url = work.get("doi") or location.get("landing_page_url") or work["id"]
        citations = work.get("cited_by_count", 0)
        sources.append(
            Source(
                title=work["display_name"],
                url=url,
                year=work.get("publication_year"),
                snippet=f"Academic work with {citations:,} citations indexed by OpenAlex.",
                source_type="academic",
            )
        )
    return sources


async def gather_all(queries: list[str], limit: int) -> tuple[list[Source], list[Source]]:
    web_calls = [search_web(query, limit) for query in queries]
    academic_calls = [search_openalex(query, limit) for query in queries]
    results = await asyncio.gather(*web_calls, *academic_calls, return_exceptions=True)
    split = len(web_calls)

    def flatten(groups: list[object]) -> list[Source]:
        output: list[Source] = []
        seen: set[str] = set()
        for group in groups:
            if isinstance(group, Exception):
                continue
            for source in group:  # type: ignore[union-attr]
                if source.url not in seen:
                    output.append(source)
                    seen.add(source.url)
        return output

    return flatten(results[:split]), flatten(results[split:])

