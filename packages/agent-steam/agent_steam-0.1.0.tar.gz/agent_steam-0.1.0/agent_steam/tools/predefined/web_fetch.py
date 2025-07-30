from typing import Dict, Any, Optional
import asyncio
import httpx
import requests
from ..base import LocalTool

class WebFetchTool(LocalTool):
    """Web content fetching tool for retrieving and parsing web page content"""
    name: str = "web_fetch"
    description: str = """Web content fetching tool for retrieving full page content from URLs.

Features:
- Fetches HTML content from web pages and extracts readable text
- Supports content parsing and text extraction from various web page formats
- Handles common web protocols (HTTP/HTTPS) and follows redirects
- Limits returned content to 5000 characters for performance
- Useful for detailed content analysis, full article reading, and comprehensive research
- Use this tool when you need the full content of a specific web page for analysis"""
    
    async def execute(self, url: str, timeout: int = 30, extract_text: bool = True, offset: int = 0) -> Dict[str, Any]:
        """
        Fetch web content from the specified URL.
        
        Args:
            url: The URL of the web page to fetch content from
            timeout: Request timeout in seconds (default: 30)
            extract_text: Whether to extract readable text content from HTML (default: True)
            offset: Content offset position to start reading from (default: 0)
            
        Returns:
            Dict containing the fetched content and metadata
        """
        try:
            # Validate URL
            if not url or not isinstance(url, str):
                return {
                    "success": False,
                    "error": "Invalid URL provided"
                }
            
            # Ensure URL has proper protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Use httpx for async HTTP requests with fallback to requests
            try:
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    content = response.text
                    content_type = response.headers.get('content-type', '')
                    status_code = response.status_code
            except Exception:
                # Fallback to synchronous requests
                try:
                    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                    response.raise_for_status()
                    content = response.text
                    content_type = response.headers.get('content-type', '')
                    status_code = response.status_code
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to fetch content: {str(e)}"
                    }
            
            # Extract text content if requested
            if extract_text:
                try:
                    # Try to use markdownify if available
                    try:
                        import markdownify
                        content = markdownify.markdownify(content)
                    except ImportError:
                        # Simple HTML tag removal fallback
                        import re
                        # Remove script and style elements
                        content = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
                        # Remove HTML tags
                        content = re.sub(r'<[^>]+>', '', content)
                        # Clean up whitespace
                        content = re.sub(r'\s+', ' ', content).strip()
                except Exception:
                    # If text extraction fails, return raw content
                    pass
            
            # Apply offset if specified
            if offset > 0 and len(content) > offset:
                content = content[offset:]
            
            # Limit content to 5000 characters
            max_length = 5000
            truncated = False
            if len(content) > max_length:
                content = content[:max_length]
                truncated = True
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "content_type": content_type,
                "status_code": status_code,
                "content_length": len(content),
                "truncated": truncated,
                "extract_text": extract_text,
                "offset": offset
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching web content: {str(e)}"
            }