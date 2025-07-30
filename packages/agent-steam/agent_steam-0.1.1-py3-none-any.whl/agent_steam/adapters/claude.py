import os
import json
import copy
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import anthropic

from .base import LLMAdapter


class ClaudeAdapter(LLMAdapter):
    """Adapter for Anthropic Claude API"""
    
    MAX_TOKEN_LIMIT: int = 200000
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = kwargs.get("model", "claude-sonnet-4-20250514")
        self.logger = logging.getLogger(__name__)
    
    def get_input_tokens(self, response):
        """Get input token usage with cache read tokens"""
        return response.get('input_tokens', 0) + response.get('cache_read_input_tokens', 0), response.get('cache_read_input_tokens', 0), response.get('cache_creation_input_tokens', 0)
    
    def get_output_tokens(self, response):
        """Get output token usage"""
        return response.get('output_tokens', 0)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send messages to Claude and get response"""
        
        # Check if we need to compress messages based on last round's token usage
        if self.should_compress_messages():
            messages = self.compress_messages(messages)
            self.logger.info(f"Compressed messages due to high token usage: {self.last_round_usage.total_tokens} tokens")
        
        # Validate messages before formatting
        if not messages or all(not msg.get("content", "").strip() for msg in messages if msg.get("role") != "system"):
            raise ValueError("At least one non-system message must have non-empty content")
        
        # Format messages for Claude with cache support
        claude_messages = self.format_messages(messages)
        
        # Format tools for Claude with cache support
        claude_tools = self.format_tools(tools) if tools else []
        
        # Build request with cache control
        request = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": kwargs.get("max_tokens", 20000),
            "temperature": kwargs.get("temperature", 0.1),
        }
        
        if claude_tools:
            request["tools"] = claude_tools
        
        # Add system message with cache_control if it exists
        system_msg = next((m for m in messages if m["role"] == "system"), None)
        if system_msg:
            request["system"] = [{"type": "text", "text": system_msg["content"], "cache_control": {"type": "ephemeral"}}]
        elif "system" in kwargs:
            system_prompt = kwargs.pop("system")
            request["system"] = [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request:
                if key != 'tool_choice':
                    request[key] = value
                elif len(claude_tools) > 0:
                    request[key] = value
        
        try:
            # Make the API call with retry logic for rate limits
            max_retries = 3
            retry_count = 0
            wait_time = 60  # seconds
            
            while retry_count < max_retries:
                try:
                    response = self.client.messages.create(**request)
                    
                    # Extract token usage and update tracking
                    usage = response.usage
                    cache_create = getattr(usage, 'cache_creation_input_tokens', 0)
                    cache_hit = getattr(usage, 'cache_read_input_tokens', 0)
                    output = getattr(usage, 'output_tokens', 0)
                    
                    # Update token usage tracking
                    self.update_token_usage(cache_create, cache_hit, output)
                    
                    return self._parse_claude_response(response)
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"遇到Anthropic速率限制，等待{wait_time}秒后重试... ({retry_count}/{max_retries})")
                        import asyncio
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"达到最大重试次数 ({max_retries})，放弃重试")
                        raise Exception(f"Claude API error: {e}")
        except Exception as e:
            raise Exception(f"Claude API error: {e}")
    
    def _parse_claude_response(self, response) -> Dict[str, Any]:
        """Parse Claude response into standard format"""
        content = ""
        tool_calls = []
        
        for item in response.content:
            if item.type == "text":
                content += item.text
            elif item.type == "tool_use":
                tool_calls.append({
                    "id": item.id,
                    "function": {
                        "name": item.name,
                        "arguments": item.input
                    }
                })
        
        result = {"content": content}
        if tool_calls:
            result["tool_calls"] = tool_calls
        
        return result
    
    def parse_tool_call(self, response: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Parse tool calls from Claude response"""
        return response.get("tool_calls")
    
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format messages for Claude API with cache control support"""
        claude_messages = []
        
        for i, msg in enumerate(messages):
            if msg["role"] == "system":
                continue  # System messages handled separately
            
            # Check if this is the last message for cache control
            cache_hint = i >= len(messages) - 1
            claude_msg = self._format_single_message(msg, cache_hint)
            claude_messages.append(claude_msg)
        
        return claude_messages
    
    def _format_single_message(self, msg: Dict[str, Any], cache_hint: bool = False) -> Dict[str, Any]:
        """Helper method to format a single message for Claude API"""
        claude_message = {
            "role": msg["role"],
            "content": copy.deepcopy(msg.get("content", ""))
        }
        
        # Handle tool results in assistant messages
        if msg["role"] == "assistant" and "tool_calls" in msg:
            # Ensure assistant content is not empty
            assistant_content = msg.get("content", "").strip() if msg.get("content") else "[continuing execution]"
            claude_message["content"] = [{
                "type": "text",
                "text": assistant_content
            }]
            
            for tool_call in msg.get("tool_calls", []):
                tool_use = {
                    "type": "tool_use",
                    "id": tool_call.get("id", f"call_{len(claude_message['content'])}"),
                    "name": tool_call.get("function", {}).get("name", tool_call.get("name", "")),
                    "input": tool_call.get("function", {}).get("arguments", tool_call.get("arguments", {}))
                }
                claude_message["content"].append(tool_use)
        
        # Handle tool results in user messages
        elif msg["role"] == "tool":
            # Tool result message
            claude_message["role"] = "user"
            claude_message["content"] = [{
                "type": "tool_result",
                "tool_use_id": msg["tool_call_id"],
                "content": msg["content"]
            }]
        
        # Handle regular user messages
        elif msg["role"] == "user" and "tool_response" not in msg:
            if isinstance(msg["content"], str):
                # Ensure content is not empty
                content_text = msg["content"].strip() if msg["content"] else "[empty message]"
                claude_message["content"] = [{
                    "type": "text",
                    "text": content_text
                }]
            else:
                # Already formatted content
                claude_message["content"] = msg["content"]
        
        # Apply cache control to the last content item if cache_hint is True
        if cache_hint and isinstance(claude_message["content"], list) and len(claude_message["content"]) > 0:
            claude_message["content"][-1] = copy.deepcopy(claude_message["content"][-1])
            claude_message["content"][-1]["cache_control"] = {"type": "ephemeral"}
        
        return claude_message
    
    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tools for Claude API with cache control support"""
        claude_tools = []
        
        for i, tool in enumerate(tools):
            claude_tool = {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "input_schema": tool["function"]["parameters"]
            }
            
            # Add cache_control to the last tool (commented out for now as it may not be needed)
            # if i == len(tools) - 1:
            #     claude_tool["cache_control"] = {"type": "ephemeral"}
            
            claude_tools.append(claude_tool)
        
        return claude_tools
    
    def format_request(self, 
                       messages: List[Dict[str, str]], 
                       tools: List[Dict[str, Any]],
                       model: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Format a request for Claude API with tools.
        
        Args:
            messages: List of message objects representing chat history
            tools: List of tool definitions available to Claude
            model: Claude model identifier (defaults to claude-sonnet-4-20250514 if not specified)
            **kwargs: Additional Claude-specific parameters
            
        Returns:
            Dict containing the formatted Claude API request payload
        """
        # Convert tools to Claude's tool format
        claude_tools = []
        for i, tool in enumerate(tools):
            claude_tool = {
                "name": tool.get("function", tool).get("name", tool.get("name", "")),
                "description": tool.get("function", tool).get("description", tool.get("description", "")),
                "input_schema": tool.get("function", tool).get("parameters", tool.get("input_schema", {}))
            }
            claude_tools.append(claude_tool)
        
        # Format the messages for Claude API
        claude_messages = []
        for i, msg in enumerate(messages):
            claude_message = self._format_single_message(msg, i >= len(messages) - 1)
            claude_messages.append(claude_message)
            
        # Build the complete request
        request = {
            "model": model or self.model,
            "messages": claude_messages,
            "tools": claude_tools,
            "max_tokens": kwargs.get("max_tokens", 20000),
            "temperature": kwargs.get("temperature", 0.1),
        }
        
        # Add system message with cache_control if it exists
        if "system" in kwargs:
            system_prompt = kwargs.pop("system")
            request["system"] = [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request:
                if key != 'tool_choice':
                    request[key] = value
                elif len(claude_tools) > 0:
                    request[key] = value
                    
        return request
    
    def format_tool_result(self, tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a tool execution result for sending back to Claude.
        
        Args:
            tool_name: Name of the tool that was executed
            result: Result data from the tool execution
            
        Returns:
            Dict formatted for Claude API containing the tool result
        """
        # Convert result object to a string for Claude
        result_str = ""
        if isinstance(result, dict):
            if "error" in result:
                result_str = f"Error: {result['error']}"
            elif "result" in result:
                result_content = result["result"]
                if isinstance(result_content, (dict, list)):
                    result_str = json.dumps(result_content, indent=2)
                else:
                    result_str = str(result_content)
            else:
                result_str = json.dumps(result, indent=2)
        else:
            result_str = str(result)
        
        return {
            "type": "tool_result",
            "tool_use_id": result.get("id", "unknown"),
            "content": result_str
        }
    
    def parse_response(self, response: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], bool]:
        """
        Parse Claude API response to extract thinking, tool calls, and termination status.
        
        Args:
            response: Raw response from Claude API
            
        Returns:
            Tuple containing:
            - Thinking content (str): Claude's reasoning/explanation
            - Tool calls (List[Dict]): List of tools Claude wants to execute
            - Is terminated (bool): True if no more tool calls (Claude is done)
        """
        content = response.get("content", [])
        
        # Initialize variables
        thinking = ""
        tool_calls = []
        is_terminated = True  # Default to terminated unless we find tool calls
        
        # Extract text and tool calls from the response
        for item in content:
            if item["type"] == "text":
                thinking += item["text"]
            
            elif item["type"] == "tool_use":
                is_terminated = False  # If there's a tool call, not terminated
                tool_call = {
                    "id": item.get("id", f"call_{len(tool_calls)}"),
                    "name": item["name"],
                    "arguments": item["input"]
                }
                tool_calls.append(tool_call)
        
        if len(thinking) == 0:
            thinking = '<继续执行之前的命令>'
        
        return thinking, tool_calls, is_terminated
    
    def call_llm(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the Claude API with the formatted request.
        
        Args:
            request: The formatted request payload for the Claude API
            
        Returns:
            Raw response from the Claude API
        """
        # Make the API call with retry logic for rate limits
        max_retries = 3
        retry_count = 0
        wait_time = 60  # seconds
        
        while retry_count < max_retries:
            try:
                response = json.loads(self.client.messages.create(**request).json())
                return response
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"遇到Anthropic速率限制，等待{wait_time}秒后重试... ({retry_count}/{max_retries})")
                    import time
                    time.sleep(wait_time)
                else:
                    print(f"达到最大重试次数 ({max_retries})，放弃重试")
                    raise