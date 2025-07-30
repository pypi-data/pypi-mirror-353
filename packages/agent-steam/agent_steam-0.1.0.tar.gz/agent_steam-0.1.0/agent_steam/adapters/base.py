from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class LLMAdapter(ABC):
    """Base class for LLM adapters"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
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