from typing import Dict, Type, List
from .base import LLMAdapter
from .claude import ClaudeAdapter
from .deepseek import DeepSeekAdapter


class AdapterRegistry:
    """Registry for LLM adapters"""
    
    def __init__(self):
        self._adapters: Dict[str, Type[LLMAdapter]] = {
            "claude": ClaudeAdapter,
            "deepseek": DeepSeekAdapter,
        }
    
    def register_adapter(self, name: str, adapter_class: Type[LLMAdapter]) -> None:
        """Register a new adapter"""
        self._adapters[name] = adapter_class
    
    def get_adapter(self, name: str) -> LLMAdapter:
        """Get an adapter instance by name"""
        if name not in self._adapters:
            raise ValueError(f"Unknown adapter: {name}. Available: {list(self._adapters.keys())}")
        
        adapter_class = self._adapters[name]
        return adapter_class()
    
    def list_adapters(self) -> List[str]:
        """List available adapter names"""
        return list(self._adapters.keys())