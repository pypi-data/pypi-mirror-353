import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import openai

from .base import LLMAdapter


class DeepSeekAdapter(LLMAdapter):
    """Adapter for DeepSeek API"""
    
    MAX_TOKEN_LIMIT: int = 65536
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = kwargs.get("model", "deepseek-chat")
        self.logger = logging.getLogger(__name__)
    
    def get_input_tokens(self, response):
        """Get input token usage"""
        usage = response.get('usage', {})
        return usage.get('prompt_tokens', 0), 0, 0
    
    def get_output_tokens(self, response):
        """Get output token usage"""
        usage = response.get('usage', {})
        return usage.get('completion_tokens', 0)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send messages to DeepSeek and get response"""
        
        # Check if we need to compress messages based on last round's token usage
        if self.should_compress_messages():
            messages = self.compress_messages(messages)
            self.logger.info(f"Compressed messages due to high token usage: {self.last_round_usage.total_tokens} tokens")
        
        # Validate messages before formatting
        if not messages or all(not msg.get("content", "").strip() for msg in messages if msg.get("role") != "system"):
            raise ValueError("At least one non-system message must have non-empty content")
        
        # Format messages for DeepSeek
        deepseek_messages = self.format_messages(messages)
        
        # Format tools for DeepSeek
        deepseek_tools = self.format_tools(tools) if tools else []
        
        # Build request
        request = {
            "model": self.model,
            "messages": deepseek_messages,
            "max_tokens": kwargs.get("max_tokens", 8000),
            "temperature": kwargs.get("temperature", 0.1),
        }
        
        if deepseek_tools:
            request["tools"] = deepseek_tools
        
        # Add system message if it exists
        system_msg = next((m for m in messages if m["role"] == "system"), None)
        if system_msg:
            system_message = {
                "role": "system",
                "content": system_msg["content"]
            }
            request["messages"].insert(0, system_message)
        elif "system" in kwargs:
            system_prompt = kwargs.pop("system")
            system_message = {
                "role": "system",
                "content": system_prompt
            }
            request["messages"].insert(0, system_message)
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request:
                if key != 'tool_choice':
                    request[key] = value
                elif len(deepseek_tools) > 0:
                    request[key] = value
        
        try:
            # Make the API call with retry logic for rate limits
            max_retries = 3
            retry_count = 0
            wait_time = 60  # seconds
            
            while retry_count < max_retries:
                try:
                    response = self.client.chat.completions.create(**request)
                    
                    # Extract token usage and update tracking
                    usage = response.usage
                    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                    completion_tokens = getattr(usage, 'completion_tokens', 0)
                    
                    # Update token usage tracking
                    self.update_token_usage(prompt_tokens, 0, completion_tokens)
                    
                    return self._parse_deepseek_response(response)
                except Exception as e:
                    if "rate_limit" in str(e).lower() or "per minute" in str(e).lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"遇到DeepSeek速率限制，等待{wait_time}秒后重试... ({retry_count}/{max_retries})")
                            import asyncio
                            await asyncio.sleep(wait_time)
                        else:
                            print(f"达到最大重试次数 ({max_retries})，放弃重试")
                            raise Exception(f"DeepSeek API error: {e}")
                    else:
                        raise Exception(f"DeepSeek API error: {e}")
        except Exception as e:
            raise Exception(f"DeepSeek API error: {e}")
    
    def _parse_deepseek_response(self, response) -> Dict[str, Any]:
        """Parse DeepSeek response into standard format"""
        if not response.choices:
            raise ValueError("Invalid response format from DeepSeek API")
        
        message = response.choices[0].message
        content = message.content or ""
        tool_calls = []
        
        # Extract tool calls
        raw_tool_calls = message.tool_calls or []
        for tool_call in raw_tool_calls:
            if tool_call.type == "function":
                function = tool_call.function
                # Try to parse arguments as JSON
                try:
                    arguments = json.loads(function.arguments)
                except json.JSONDecodeError:
                    arguments = function.arguments
                
                tool_calls.append({
                    "id": tool_call.id,
                    "function": {
                        "name": function.name,
                        "arguments": arguments
                    }
                })
        
        result = {"content": content}
        if tool_calls:
            result["tool_calls"] = tool_calls
        
        return result
    
    def parse_tool_call(self, response: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Parse tool calls from DeepSeek response"""
        return response.get("tool_calls")
    
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format messages for DeepSeek API"""
        deepseek_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                continue  # System messages handled separately
            
            deepseek_msg = self._format_single_message(msg)
            if deepseek_msg:
                deepseek_messages.append(deepseek_msg)
        
        return deepseek_messages
    
    def _format_single_message(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper method to format a single message for DeepSeek API"""
        deepseek_message = {
            "role": msg["role"],
            "content": msg.get("content", "")
        }
        
        # Handle tool calls in assistant messages
        if msg["role"] == "assistant" and "tool_calls" in msg:
            # Ensure assistant content is not empty
            assistant_content = msg.get("content", "").strip() if msg.get("content") else "[continuing execution]"
            deepseek_message["content"] = assistant_content
            
            tool_calls = []
            for tool_call in msg.get("tool_calls", []):
                tool_calls.append({
                    "id": tool_call.get("id", f"call_{len(tool_calls)}"),
                    "type": "function",
                    "function": {
                        "name": tool_call.get("function", {}).get("name", tool_call.get("name", "")),
                        "arguments": json.dumps(tool_call.get("function", {}).get("arguments", tool_call.get("arguments", {})))
                    }
                })
            
            if tool_calls:
                deepseek_message["tool_calls"] = tool_calls
        
        # Handle tool results
        elif msg["role"] == "tool":
            # Tool result message - convert to DeepSeek format
            return {
                "role": "tool",
                "tool_call_id": msg["tool_call_id"],
                "content": msg["content"]
            }
        
        # Handle regular user messages
        elif msg["role"] == "user":
            if isinstance(msg["content"], str):
                # Ensure content is not empty
                content_text = msg["content"].strip() if msg["content"] else "[empty message]"
                deepseek_message["content"] = content_text
            else:
                # Handle complex content
                deepseek_message["content"] = msg["content"]
        
        return deepseek_message
    
    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tools for DeepSeek API"""
        deepseek_tools = []
        
        for tool in tools:
            deepseek_tool = {
                "type": "function",
                "function": {
                    "name": tool["function"]["name"],
                    "description": tool["function"]["description"],
                    "parameters": tool["function"]["parameters"]
                }
            }
            deepseek_tools.append(deepseek_tool)
        
        return deepseek_tools
    
    def format_request(self, 
                       messages: List[Dict[str, str]], 
                       tools: List[Dict[str, Any]],
                       model: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Format a request for DeepSeek API with tools.
        
        Args:
            messages: List of message objects representing chat history
            tools: List of tool definitions available to DeepSeek
            model: DeepSeek model identifier (defaults to deepseek-chat if not specified)
            **kwargs: Additional DeepSeek-specific parameters
            
        Returns:
            Dict containing the formatted DeepSeek API request payload
        """
        # Convert tools to DeepSeek's tool format
        deepseek_tools = self.format_tools(tools)
        
        # Format the messages for DeepSeek API
        deepseek_messages = self.format_messages(messages)
            
        # Build the complete request
        request = {
            "model": model or self.model,
            "messages": deepseek_messages,
            "tools": deepseek_tools,
            "max_tokens": kwargs.get("max_tokens", 8000),
            "temperature": kwargs.get("temperature", 0.1),
        }
        
        # Add system message if it exists
        if "system" in kwargs:
            system_prompt = kwargs.pop("system")
            system_message = {
                "role": "system",
                "content": system_prompt
            }
            request["messages"].insert(0, system_message)
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request:
                if key != 'tool_choice':
                    request[key] = value
                elif len(deepseek_tools) > 0:
                    request[key] = value
                    
        return request
    
    def format_tool_result(self, tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a tool execution result for sending back to DeepSeek.
        
        Args:
            tool_name: Name of the tool that was executed (not used in DeepSeek format)
            result: Result data from the tool execution
            
        Returns:
            Dict formatted for DeepSeek API containing the tool result
        """
        # Convert result object to a string for DeepSeek
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
            "tool_call_id": result.get("id", "unknown"),
            "content": result_str
        }
    
    def parse_response(self, response: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], bool]:
        """
        Parse DeepSeek API response to extract thinking, tool calls, and termination status.
        
        Args:
            response: Raw response from DeepSeek API
            
        Returns:
            Tuple containing:
            - Thinking content (str): DeepSeek's reasoning/explanation
            - Tool calls (List[Dict]): List of tools DeepSeek wants to execute
            - Is terminated (bool): True if no more tool calls (DeepSeek is done)
        """
        if "choices" not in response or not response["choices"]:
            raise ValueError("Invalid response format from DeepSeek API")
        
        message = response["choices"][0]["message"]
        thinking = message.get("content", "") or ""
        
        # Extract tool calls
        tool_calls = []
        raw_tool_calls = message.get("tool_calls", []) or []
        
        for tool_call in raw_tool_calls:
            if tool_call["type"] == "function":
                function = tool_call["function"]
                # Try to parse arguments as JSON
                try:
                    arguments = json.loads(function["arguments"])
                except json.JSONDecodeError:
                    arguments = function["arguments"]
                
                tool_calls.append({
                    "id": tool_call["id"],
                    "name": function["name"],
                    "arguments": arguments
                })
        
        # Determine if the model is done or wants more tool execution
        is_terminated = not bool(tool_calls)
        
        if len(thinking) == 0:
            thinking = '<继续执行之前的命令>'
        
        return thinking, tool_calls, is_terminated
    
    def call_llm(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the DeepSeek API with the formatted request.
        
        Args:
            request: The formatted request payload for the DeepSeek API
            
        Returns:
            Raw response from the DeepSeek API
        """
        # Make the API call with retry logic for rate limits
        max_retries = 3
        retry_count = 0
        wait_time = 60  # seconds
        
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(**request)
                return response.model_dump()
            except Exception as e:
                # Check if it's a rate limit error
                if "rate_limit" in str(e).lower() or "per minute" in str(e).lower():
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"遇到DeepSeek速率限制，等待{wait_time}秒后重试... ({retry_count}/{max_retries})")
                        import time
                        time.sleep(wait_time)
                    else:
                        print(f"达到最大重试次数 ({max_retries})，放弃重试")
                        raise
                else:
                    # For other errors, don't retry
                    raise