import os
import json
import logging
import inspect
from typing import Dict, Any, List, Optional, Type, Union, Callable
from pathlib import Path

from .adapters.registry import AdapterRegistry
from .tools.registry import ToolRegistry
from .tools.base import LocalTool
from .mcp.client import MCPClient
from .io.manager import IOManager
from .utils.logging import setup_logging


class AgentSteam:
    _tools: List[Type[LocalTool]] = []
    _entrypoint_function: Optional[Callable] = None
    _entrypoint_module: Optional[str] = None
    _entrypoint_function_name: Optional[str] = None
    
    def __init__(
        self,
        system_prompt: str,
        llm_provider: Optional[str] = None,
        mcp_server_url: Optional[str] = None,
        mcp_auth_token: Optional[str] = None,
        input_dir: str = "/input",
        output_dir: str = "/outputs",
        logs_dir: str = "/logs"
    ):
        self.system_prompt = system_prompt
        self.llm_provider = llm_provider or os.getenv("AGENT_STEAM_LLM_PROVIDER", "claude")
        
        # Setup directories
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logs_dir = Path(logs_dir)
        
        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = setup_logging(self.logs_dir / "agent.log")
        
        # Initialize IO manager
        self.io_manager = IOManager(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            logs_dir=self.logs_dir
        )
        
        # Initialize registries
        self.adapter_registry = AdapterRegistry()
        self.tool_registry = ToolRegistry()
        
        # Setup LLM adapter
        self.adapter = self.adapter_registry.get_adapter(self.llm_provider)
        
        # Setup MCP client
        mcp_url = mcp_server_url or os.getenv("MCP_SERVER_URL")
        mcp_token = mcp_auth_token or os.getenv("MCP_AUTH_TOKEN")
        
        if mcp_url:
            self.mcp_client = MCPClient(mcp_url, mcp_token)
        else:
            self.mcp_client = None
            self.logger.warning("No MCP server configured")
        
        # Register tools
        self._register_tools()
        
        self.logger.info(f"AgentSteam initialized with {self.llm_provider} adapter")
    
    @classmethod
    def Tool(cls, tool_class: Type[LocalTool]) -> Type[LocalTool]:
        """Decorator to register tools"""
        cls._tools.append(tool_class)
        return tool_class
    
    @classmethod
    def entrypoint(cls, func: Callable) -> Callable:
        """
        Decorator to mark a function as the Docker entrypoint for the agent.
        
        Usage:
        @AgentSteam.entrypoint
        async def main():
            # Your agent logic here
            pass
        
        Args:
            func: The function to be used as the Docker entrypoint
            
        Returns:
            The original function unchanged
        """
        cls._entrypoint_function = func
        cls._entrypoint_function_name = func.__name__
        
        # Get the module where the function is defined
        module = inspect.getmodule(func)
        if module:
            cls._entrypoint_module = module.__name__
        
        return func
    
    @classmethod
    def get_entrypoint_info(cls) -> Dict[str, Optional[str]]:
        """
        Get information about the registered entrypoint function.
        
        Returns:
            Dict containing entrypoint module and function name
        """
        return {
            "module": cls._entrypoint_module,
            "function_name": cls._entrypoint_function_name,
            "has_entrypoint": cls._entrypoint_function is not None
        }
    
    def _register_tools(self) -> None:
        """Register all tools including predefined and user-defined ones"""
        # Register predefined tools
        from .tools.predefined import get_predefined_tools
        for tool_class in get_predefined_tools():
            self.tool_registry.register_tool(tool_class())
        
        # Register user-defined tools
        for tool_class in self._tools:
            self.tool_registry.register_tool(tool_class())
        
        self.logger.info(f"Registered {len(self.tool_registry.tools)} local tools")
    
    async def run(self) -> Dict[str, Any]:
        """Main execution loop"""
        try:
            # Read input
            user_input = await self.io_manager.read_input()
            self.logger.info(f"Received input: {user_input}")
            
            # Get available tools (local + MCP)
            available_tools = await self._get_available_tools()
            
            # Initialize conversation
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Main conversation loop
            max_iterations = 50
            for i in range(max_iterations):
                self.logger.info(f"Iteration {i + 1}")
                
                # Get LLM response
                response = await self.adapter.chat_completion(
                    messages=messages,
                    tools=available_tools
                )
                
                if response.get("tool_calls"):
                    # Execute tool calls
                    tool_results = await self._execute_tool_calls(response["tool_calls"])
                    
                    # Add assistant message and tool results
                    messages.append({
                        "role": "assistant", 
                        "content": response.get("content", ""),
                        "tool_calls": response["tool_calls"]
                    })
                    
                    for result in tool_results:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": result["tool_call_id"],
                            "content": result["content"]
                        })
                else:
                    # Final response
                    final_response = response.get("content", "")
                    await self.io_manager.write_output({"response": final_response})
                    
                    self.logger.info("Agent completed successfully")
                    return {"success": True, "response": final_response}
            
            # Max iterations reached
            self.logger.warning("Max iterations reached")
            await self.io_manager.write_output({"error": "Max iterations reached"})
            return {"success": False, "error": "Max iterations reached"}
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}", exc_info=True)
            await self.io_manager.write_output({"error": str(e)})
            return {"success": False, "error": str(e)}
    
    async def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools (local + MCP)"""
        tools = []
        
        # Add local tools
        for tool in self.tool_registry.tools.values():
            tools.append(tool.to_schema())
        
        # Add MCP tools
        if self.mcp_client:
            try:
                mcp_tools = await self.mcp_client.get_tools()
                tools.extend(mcp_tools)
                self.logger.info(f"Loaded {len(mcp_tools)} MCP tools")
            except Exception as e:
                self.logger.error(f"Failed to load MCP tools: {e}")
        
        return tools
    
    async def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tool calls and return results"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            tool_call_id = tool_call["id"]
            
            try:
                # Check if it's a local tool
                if tool_name in self.tool_registry.tools:
                    tool = self.tool_registry.tools[tool_name]
                    result = await tool.execute(**arguments)
                    
                # Check if it's an MCP tool
                elif self.mcp_client:
                    result = await self.mcp_client.execute_tool(tool_name, arguments)
                else:
                    result = f"Tool '{tool_name}' not found"
                
                results.append({
                    "tool_call_id": tool_call_id,
                    "content": str(result)
                })
                
                self.logger.info(f"Executed tool {tool_name} successfully")
                
            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {e}"
                self.logger.error(error_msg)
                results.append({
                    "tool_call_id": tool_call_id,
                    "content": error_msg
                })
        
        return results