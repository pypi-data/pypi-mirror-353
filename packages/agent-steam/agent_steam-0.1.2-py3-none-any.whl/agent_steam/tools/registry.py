from typing import Dict, List
from .base import LocalTool


class ToolRegistry:
    """Registry for local tools"""
    
    def __init__(self):
        self.tools: Dict[str, LocalTool] = {}
    
    def register_tool(self, tool: LocalTool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> LocalTool:
        """Get a tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]
    
    def list_tools(self) -> List[str]:
        """List available tool names"""
        return list(self.tools.keys())