from typing import Dict, Any, List, Optional
from ..base import LocalTool

class DuckDuckGoSearchTool(LocalTool):
    """Comprehensive web search tool powered by DuckDuckGo for finding current information across multiple content types"""
    name: str = "duckduckgo_search"
    description: str = """Comprehensive web search tool powered by DuckDuckGo's privacy-focused search engine.

Features:
- Searches the internet for real-time information on any topic without tracking users
- Supports four distinct search types: web pages, images, videos, and news articles
- Returns structured results with titles, URLs, snippets, and type-specific metadata
- Offers advanced filtering options including time ranges, geographic regions, languages, and safety levels
- Ideal for finding current information, recent news, visual content, or multimedia resources
- Use this tool when you need up-to-date information from the web, research assistance, fact-checking, or content discovery"""
    
    async def execute(self, query: str, search_type: str = "web", max_results: int = 10, 
                     region: Optional[str] = None, time_range: Optional[str] = None, 
                     safesearch: str = "moderate") -> Dict[str, Any]:
        """
        Perform a DuckDuckGo search with the specified parameters.
        
        Args:
            query: The search query string
            search_type: Type of search content ('web', 'images', 'videos', 'news')
            max_results: Maximum number of results to return (1-50)
            region: Geographic region for localized results (e.g., 'us-en', 'uk-en')
            time_range: Filter by publication time ('d', 'w', 'm', 'y')
            safesearch: Content filtering level ('strict', 'moderate', 'off')
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            # Validate input parameters
            if not query or not isinstance(query, str):
                return {
                    "success": False,
                    "error": "Invalid search query provided"
                }
            
            if search_type not in ["web", "images", "videos", "news"]:
                return {
                    "success": False,
                    "error": f"Invalid search type: {search_type}. Must be one of: web, images, videos, news"
                }
            
            if not (1 <= max_results <= 50):
                return {
                    "success": False,
                    "error": "max_results must be between 1 and 50"
                }
            
            if time_range and time_range not in ["d", "w", "m", "y"]:
                return {
                    "success": False,
                    "error": "time_range must be one of: d, w, m, y"
                }
            
            if safesearch not in ["strict", "moderate", "off"]:
                return {
                    "success": False,
                    "error": "safesearch must be one of: strict, moderate, off"
                }
            
            # Try to import duckduckgo_search
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                return {
                    "success": False,
                    "error": "duckduckgo_search package is not installed. Please install it with: pip install duckduckgo_search"
                }
            
            # Initialize DDGS client
            ddgs = DDGS()
            
            # Prepare search parameters
            search_params = {
                "max_results": max_results,
                "safesearch": safesearch
            }
            
            if region:
                search_params["region"] = region
            
            if time_range:
                search_params["timelimit"] = time_range
            
            # Perform search based on type
            results = []
            try:
                if search_type == "web":
                    search_results = ddgs.text(query, **search_params)
                elif search_type == "images":
                    search_results = ddgs.images(query, **search_params)
                elif search_type == "videos":
                    search_results = ddgs.videos(query, **search_params)
                elif search_type == "news":
                    search_results = ddgs.news(query, **search_params)
                
                # Convert generator to list and ensure we don't exceed max_results
                results = list(search_results)[:max_results]
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Search failed: {str(e)}"
                }
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_result = {
                    "rank": i + 1,
                    "title": result.get("title", ""),
                    "url": result.get("href") or result.get("url", ""),
                    "snippet": result.get("body") or result.get("description", ""),
                }
                
                # Add type-specific fields
                if search_type == "images":
                    formatted_result.update({
                        "image_url": result.get("image", ""),
                        "thumbnail": result.get("thumbnail", ""),
                        "width": result.get("width"),
                        "height": result.get("height")
                    })
                elif search_type == "videos":
                    formatted_result.update({
                        "duration": result.get("duration", ""),
                        "published": result.get("published", ""),
                        "publisher": result.get("publisher", "")
                    })
                elif search_type == "news":
                    formatted_result.update({
                        "date": result.get("date", ""),
                        "source": result.get("source", "")
                    })
                
                formatted_results.append(formatted_result)
            
            return {
                "success": True,
                "query": query,
                "search_type": search_type,
                "total_results": len(formatted_results),
                "max_results": max_results,
                "region": region,
                "time_range": time_range,
                "safesearch": safesearch,
                "results": formatted_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error during DuckDuckGo search: {str(e)}"
            }