import httpx
from typing import Dict, Any, List, Optional
import logging


class MCPClient:
    """Client for connecting to MCP servers"""
    
    def __init__(self, server_url: str, auth_token: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        self.auth_token = auth_token
        self.logger = logging.getLogger(__name__)
        
        # Setup HTTP client
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        self.client = httpx.AsyncClient(headers=headers, timeout=30.0)
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from MCP server"""
        try:
            response = await self.client.get(f"{self.server_url}/api/mcp/tools")
            response.raise_for_status()
            
            data = response.json()
            if not data.get("success"):
                raise Exception(f"MCP server error: {data.get('error', 'Unknown error')}")
            
            tools = data.get("data", {}).get("tools", [])
            
            # Convert MCP tools to OpenAI function calling format
            formatted_tools = []
            for tool in tools:
                formatted_tool = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool.get("parameters", {})
                    }
                }
                formatted_tools.append(formatted_tool)
            
            return formatted_tools
            
        except Exception as e:
            self.logger.error(f"Failed to get MCP tools: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool on the MCP server"""
        try:
            payload = {
                "name": tool_name,
                "arguments": arguments
            }
            
            response = await self.client.post(
                f"{self.server_url}/api/mcp/execute",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get("success"):
                raise Exception(f"MCP execution error: {data.get('error', 'Unknown error')}")
            
            result = data.get("data", {})
            
            # Format result
            if result.get("isError"):
                return f"Error: {result.get('content', [{}])[0].get('text', 'Unknown error')}"
            
            content_items = result.get("content", [])
            if content_items:
                return content_items[0].get("text", "No result")
            
            return "Tool executed successfully"
            
        except Exception as e:
            self.logger.error(f"Failed to execute MCP tool {tool_name}: {e}")
            return f"Error executing tool: {e}"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()