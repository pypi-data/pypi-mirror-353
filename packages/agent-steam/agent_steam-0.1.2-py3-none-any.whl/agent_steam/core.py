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
    _preprocess_function: Optional[Callable] = None
    _postprocess_function: Optional[Callable] = None
    _global_variables: Dict[str, Any] = {}
    
    def __init__(
        self,
        system_prompt: str,
        llm_provider: Optional[str] = None,
        mcp_server_url: Optional[str] = None,
        mcp_auth_token: Optional[str] = None,
        input_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        logs_dir: Optional[str] = None,
        root_dir: Optional[str] = None,
        predefined_tools: Optional[List[str]] = None
    ):
        self.system_prompt = system_prompt
        self.llm_provider = llm_provider or os.getenv("AGENT_STEAM_LLM_PROVIDER", "claude")
        
        # Setup directories with configurable root path
        root_path = Path(root_dir or os.getenv("AGENT_STEAM_ROOT_DIR", "/"))
        
        self.input_dir = Path(input_dir or root_path / "input")
        self.output_dir = Path(output_dir or root_path / "outputs") 
        self.logs_dir = Path(logs_dir or root_path / "logs")
        
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
        
        # Store predefined tools selection
        self.predefined_tools = predefined_tools
        
        # Register tools
        self._register_tools()
        
        self.logger.info(f"AgentSteam initialized with {self.llm_provider} adapter")
    
    @classmethod
    def Tool(cls, tool_class: Type[LocalTool]) -> Type[LocalTool]:
        """Decorator to register tools"""
        cls._tools.append(tool_class)
        return tool_class
    
    @classmethod
    def preProcess(cls, func: Callable) -> Callable:
        """
        Decorator to register a preprocessing function.
        
        The function should accept input_dir as parameter and return str (initial user message).
        
        Usage:
        @AgentSteam.preProcess
        def my_preprocess(input_dir: str) -> str:
            # Process input folder content
            return "Initial user message"
        """
        cls._preprocess_function = func
        return func
    
    @classmethod
    def postProcess(cls, func: Callable) -> Callable:
        """
        Decorator to register a postprocessing function.
        
        The function should accept outputs_dir as parameter and have no return value.
        
        Usage:
        @AgentSteam.postProcess
        def my_postprocess(outputs_dir: str) -> None:
            # Export outputs to folder
            pass
        """
        cls._postprocess_function = func
        return func
    
    @classmethod
    def GlobalVariable(cls, **variables) -> None:
        """
        Set global variables that can be accessed by tools.
        
        Usage:
        AgentSteam.GlobalVariable(api_key="value", config={"key": "value"})
        """
        cls._global_variables.update(variables)
    
    @classmethod
    def getGlobalVariable(cls, key: str, default: Any = None) -> Any:
        """
        Get a global variable value.
        
        Args:
            key: Variable key
            default: Default value if key not found
            
        Returns:
            Variable value or default
        """
        return cls._global_variables.get(key, default)
    
    @classmethod
    def setGlobalVariable(cls, key: str, value: Any) -> None:
        """
        Set a global variable value.
        
        Args:
            key: Variable key
            value: Variable value
        """
        cls._global_variables[key] = value
    
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
        # Register predefined tools (filtered if specified)
        from .tools.predefined import get_predefined_tools
        predefined_tool_classes = get_predefined_tools()
        
        if self.predefined_tools is not None:
            # Filter predefined tools based on selection
            filtered_tools = []
            for tool_class in predefined_tool_classes:
                tool_name = tool_class.__name__.lower().replace("tool", "")
                if tool_name in self.predefined_tools:
                    filtered_tools.append(tool_class)
            predefined_tool_classes = filtered_tools
        
        for tool_class in predefined_tool_classes:
            tool_instance = tool_class()
            # Pass logger to tool if it accepts it
            if hasattr(tool_instance, 'logger'):
                tool_instance.logger = self.logger
            self.tool_registry.register_tool(tool_instance)
        
        # Register user-defined tools
        for tool_class in self._tools:
            tool_instance = tool_class()
            # Pass logger to tool if it accepts it
            if hasattr(tool_instance, 'logger'):
                tool_instance.logger = self.logger
            self.tool_registry.register_tool(tool_instance)
        
        self.logger.info(f"Registered {len(self.tool_registry.tools)} local tools")
    
    async def run(self) -> Dict[str, Any]:
        """Main execution loop"""
        try:
            # Check for preprocessing function
            if self.__class__._preprocess_function:
                self.logger.info("Running preprocessing function")
                user_input = self.__class__._preprocess_function(str(self.input_dir))
                self.logger.info(f"Preprocessed input: {user_input}")
            else:
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
            max_iterations = 1000
            for i in range(max_iterations):
                self.logger.info(f"Iteration {i + 1}")
                
                # Log token usage from previous round if available
                if hasattr(self.adapter, 'last_round_usage') and self.adapter.last_round_usage:
                    usage = self.adapter.last_round_usage
                    self.logger.info(f"Previous round token usage - Cache create: {usage.cache_create_tokens}, "
                                   f"Cache hit: {usage.cache_hit_tokens}, Output: {usage.output_tokens}, "
                                   f"Total: {usage.total_tokens}")
                
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
                    
                    # Check for postprocessing function
                    if self.__class__._postprocess_function:
                        self.logger.info("Running postprocessing function")
                        self.__class__._postprocess_function(str(self.output_dir))
                        self.logger.info("Postprocessing completed")
                    
                    # Log final token usage summary
                    self._log_final_token_usage()
                    
                    self.logger.info("Agent completed successfully")
                    return {"success": True, "response": final_response}
            
            # Max iterations reached
            self.logger.warning("Max iterations reached")
            await self.io_manager.write_output({"error": "Max iterations reached"})
            
            # Run postprocessing even on failure if defined
            if self.__class__._postprocess_function:
                self.logger.info("Running postprocessing function (after max iterations)")
                self.__class__._postprocess_function(str(self.output_dir))
            
            # Log final token usage summary
            self._log_final_token_usage()
            
            return {"success": False, "error": "Max iterations reached"}
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}", exc_info=True)
            await self.io_manager.write_output({"error": str(e)})
            
            # Run postprocessing even on error if defined
            if self.__class__._postprocess_function:
                try:
                    self.logger.info("Running postprocessing function (after error)")
                    self.__class__._postprocess_function(str(self.output_dir))
                except Exception as post_e:
                    self.logger.error(f"Postprocessing failed: {post_e}")
            
            # Log final token usage summary
            self._log_final_token_usage()
            
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
    
    def _log_final_token_usage(self) -> None:
        """Log final cumulative token usage statistics"""
        if hasattr(self.adapter, 'total_usage') and self.adapter.total_usage:
            total = self.adapter.total_usage
            self.logger.info("=== FINAL TOKEN USAGE SUMMARY ===")
            self.logger.info(f"Total Cache Create Tokens: {total.cache_create_tokens}")
            self.logger.info(f"Total Cache Hit Tokens: {total.cache_hit_tokens}")
            self.logger.info(f"Total Output Tokens: {total.output_tokens}")
            self.logger.info(f"Total Tokens Used: {total.total_tokens}")
            self.logger.info("================================")