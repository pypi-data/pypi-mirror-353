from typing import List, Dict, Any
from urllib.parse import urlencode

import feedparser
from fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR

# Create an MCP server instance
mcp = FastMCP("Google News Server")

# Google News RSS base URLs
GOOGLE_NEWS_BASE_URL = "https://news.google.com/rss"
GOOGLE_NEWS_SEARCH_URL = f"{GOOGLE_NEWS_BASE_URL}/search"
GOOGLE_NEWS_TOPICS_URL = f"{GOOGLE_NEWS_BASE_URL}/headlines/section/topic"


def parse_feed_entries(entries: List[Any], limit: int) -> List[Dict[str, Any]]:
    """
    Parse RSS feed entries and return structured news articles.

    Args:
        entries: List of RSS feed entries
        limit: Maximum number of articles to return

    Returns:
        List of dictionaries containing article information
    """
    articles = []

    for i, entry in enumerate(entries[:limit]):
        article = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "description": entry.get("summary", ""),
            "source": entry.get("source", {}).get("title", "") if "source" in entry else "",
        }

        # Clean up the description (remove HTML tags if present)
        if article["description"]:
            # Simple HTML tag removal
            import re
            article["description"] = re.sub(
                '<[^<]+?>', '', article["description"])

        articles.append(article)

    return articles


@mcp.tool()
async def google_news_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for news articles using a query.

    This function searches Google News RSS feed for articles matching the query.
    Region is limited to Japan.

    Args:
        query: Search query string
        limit: Maximum number of articles to return (default: 10)

    Returns:
        List of news articles with title, link, published date, description, and source

    Raises:
        McpError: When query is invalid or fetching fails
    """
    # Validate query parameter
    if not query or not isinstance(query, str):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Query parameter is required and must be a non-empty string"
        ))

    # Validate limit parameter
    if not isinstance(limit, int) or limit < 1:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Limit must be a positive integer"
        ))

    try:
        # Build the search URL with query parameters for Japan
        params = {
            "q": query,
            "hl": "ja",  # Language (Japanese)
            "gl": "JP",  # Geographic location (Japan)
            "ceid": "JP:ja"  # Country and language ID
        }

        url = f"{GOOGLE_NEWS_SEARCH_URL}?{urlencode(params)}"

        # Parse the RSS feed
        feed = feedparser.parse(url)

        # Check for feed parsing errors
        if feed.bozo:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to parse RSS feed: {feed.bozo_exception}"
            ))

        # Parse and return the entries
        return parse_feed_entries(feed.entries, limit)

    except McpError:
        raise
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error while searching Google News: {str(e)}"
        ))


@mcp.tool()
async def google_news_topics(topic_id: str = "TOP", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get news articles by topic (Japan region only).

    This function fetches news articles from a specific Google News topic.
    Region is limited to Japan.

    Available topics:
    - TOP (トップニュース - default)
    - NATION (国内)
    - WORLD (国際)
    - BUSINESS (ビジネス)
    - TECHNOLOGY (テクノロジー)
    - ENTERTAINMENT (エンタメ)
    - SPORTS (スポーツ)
    - SCIENCE (科学)
    - HEALTH (健康)

    Args:
        topic_id: Topic ID for specific news category (default: TOP)
        limit: Maximum number of articles to return (default: 10)

    Returns:
        List of news articles with title, link, published date, description, and source

    Raises:
        McpError: When topic_id is invalid or fetching fails
    """
    # Validate topic_id parameter
    if not topic_id or not isinstance(topic_id, str):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Topic ID parameter must be a non-empty string"
        ))

    # Validate limit parameter
    if not isinstance(limit, int) or limit < 1:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Limit must be a positive integer"
        ))

    try:
        # Build the topic URL for Japan
        if topic_id == "TOP":
            url = f"{GOOGLE_NEWS_BASE_URL}?hl=ja&gl=JP&ceid=JP:ja"
        else:
            url = f"{GOOGLE_NEWS_TOPICS_URL}/{topic_id}?hl=ja&gl=JP&ceid=JP:ja"

        # Parse the RSS feed
        feed = feedparser.parse(url)

        # Check for feed parsing errors
        if feed.bozo:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to parse RSS feed: {feed.bozo_exception}"
            ))

        # Check if feed is empty (might indicate invalid topic ID)
        if not feed.entries:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message="No articles found. The topic ID might be invalid."
            ))

        # Parse and return the entries
        return parse_feed_entries(feed.entries, limit)

    except McpError:
        raise
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error while fetching topic news: {str(e)}"
        ))
