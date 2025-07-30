from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class TokenUsage:
    """Token usage statistics for a single round"""
    def __init__(self):
        self.cache_create_tokens = 0
        self.cache_hit_tokens = 0
        self.output_tokens = 0
        
    @property
    def total_tokens(self) -> int:
        return self.cache_create_tokens + self.cache_hit_tokens + self.output_tokens


class LLMAdapter(ABC):
    """Base class for LLM adapters"""
    
    MAX_TOKEN_LIMIT: int = 100000  # Default limit, override in subclasses
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.last_round_usage: Optional[TokenUsage] = None
        self.total_usage: TokenUsage = TokenUsage()  # Cumulative usage across all rounds
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send messages to LLM and get response
        
        Returns:
            {
                "content": "response text",
                "tool_calls": [  # Optional
                    {
                        "id": "call_id",
                        "function": {
                            "name": "tool_name",
                            "arguments": {...}
                        }
                    }
                ]
            }
        """
        pass
    
    @abstractmethod
    def parse_tool_call(self, response: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Parse tool calls from LLM response"""
        pass
    
    @abstractmethod
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format messages for this LLM provider"""
        pass
    
    @abstractmethod
    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tools for this LLM provider"""
        pass
    
    def should_compress_messages(self) -> bool:
        """Check if messages should be compressed based on token usage"""
        if self.last_round_usage is None:
            return False
        
        threshold = self.MAX_TOKEN_LIMIT * 0.9
        return self.last_round_usage.total_tokens > threshold
    
    def compress_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compress messages to reduce token count"""
        if len(messages) <= 2:  # Keep system and first user message
            return messages
            
        compressed = [messages[0]]  # Keep system message
        
        # Keep only the last few messages (recent context)
        recent_count = min(6, len(messages) - 1)  # Keep last 6 messages
        compressed.extend(messages[-recent_count:])
        
        # Add a note about compression
        if len(compressed) < len(messages):
            compression_note = {
                "role": "user", 
                "content": f"[Previous {len(messages) - len(compressed)} messages compressed due to token limit]"
            }
            compressed.insert(1, compression_note)
        
        return compressed
    
    def update_token_usage(self, cache_create: int, cache_hit: int, output: int) -> None:
        """Update token usage statistics for the current round and add to total"""
        self.last_round_usage = TokenUsage()
        self.last_round_usage.cache_create_tokens = cache_create
        self.last_round_usage.cache_hit_tokens = cache_hit
        self.last_round_usage.output_tokens = output
        
        # Add to cumulative total
        self.total_usage.cache_create_tokens += cache_create
        self.total_usage.cache_hit_tokens += cache_hit
        self.total_usage.output_tokens += output