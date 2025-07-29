import json
import os

import httpx
import llm


class SearXNG:
    """A tool for searching the web using SearXNG search engine"""

    def __init__(self, base_url: str = None):
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = llm.get_key(explicit_key="searxng_url", key_alias="searxng_url", env_var="SEARXNG_URL")

        if not self.base_url:
            raise ValueError(
                "SearXNG URL is required. Set via SEARXNG_URL environment variable or use 'llm key set searxng_url <URL>'"
            )

        # Get method from environment variable, default to POST
        self.method = os.getenv("SEARXNG_METHOD", "POST").upper()

    def search(
        self,
        query: str,
        format: str = "json",
        categories: str = "",
        engines: str = "",
        language: str = "en",
        pageno: int = 1,
        time_range: str = "",
        safesearch: int = 1,
    ) -> str:
        """
        Search the web using SearXNG.

        Args:
            query: The search query (required)
            format: Output format (json, csv, rss) - default: json
            categories: Comma separated list of search categories (optional)
            engines: Comma separated list of search engines (optional)
            language: Language code - default: en
            pageno: Search page number - default: 1
            time_range: Time range (day, month, year) - optional
            safesearch: Safe search level (0, 1, 2) - default: 1
        """
        search_url = f"{self.base_url.rstrip('/')}/search"

        params = {
            "q": query,
            "format": format,
            "language": language,
            "pageno": pageno,
            "safesearch": safesearch,
        }

        if categories:
            params["categories"] = categories
        if engines:
            params["engines"] = engines
        if time_range:
            params["time_range"] = time_range

        try:
            # TODO: Set user agent?
            headers = {}

            with httpx.Client(follow_redirects=True, timeout=30.0, headers=headers) as client:
                if self.method == "POST":
                    # print("POST -> ", search_url, params)
                    response = client.post(search_url, data=params)
                else:
                    # print("GET -> ", search_url, params)
                    response = client.get(search_url, params=params)
                response.raise_for_status()

                if format == "json":
                    result = response.json()
                    if "results" in result:
                        formatted_results = []
                        for item in result["results"][:10]:
                            formatted_result = {
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("content", ""),
                                "engine": item.get("engine", ""),
                            }
                            formatted_results.append(formatted_result)

                        summary = {
                            "query": query,
                            "number_of_results": len(result.get("results", [])),
                            "results": formatted_results,
                        }
                        return json.dumps(summary, indent=2)
                    else:
                        return json.dumps(result, indent=2)
                else:
                    return response.text

        except httpx.HTTPError as e:
            raise Exception(f"HTTP error occurred: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing JSON response: {e}")
        except Exception as e:
            raise Exception(f"Error performing search: {e}")


def searxng_search(query: str) -> str:
    """
    Search the web using SearXNG. Returns a JSON string with results including
    title, URL, snippet, and search engine used.

    Args:
        query: Search query to search for. SearxNG search syntax (https://docs.searxng.org/user/search-syntax.html) is supported.
    """
    searxng = SearXNG()
    return searxng.search(query)


@llm.hookimpl
def register_tools(register):
    try:
        SearXNG()
        register(searxng_search)
    except ValueError as e:
        raise RuntimeError(str(e))
