from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
import inspect
import re
import json
import logging


class LocalTool(ABC):
    """Base class for local tools"""
    
    name: str = ""
    description: str = ""
    
    def __init__(self):
        if not self.name:
            self.name = self.__class__.__name__.lower().replace("tool", "")
        if not self.description:
            self.description = f"Execute {self.name}"
        
        # Logger will be set by AgentSteam when registering the tool
        self.logger: Optional[logging.Logger] = None
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments"""
        pass
    
    def _parse_docstring_schema(self) -> Dict[str, Any]:
        """Parse schema information from docstring"""
        docstring = inspect.getdoc(self.execute)
        if not docstring:
            return {}
        
        schema_info = {}
        
        # Look for @schema: {...} blocks in docstring
        # Use a more sophisticated approach to match balanced braces
        schema_start = docstring.find('@schema:')
        if schema_start != -1:
            # Find the opening brace
            brace_start = docstring.find('{', schema_start)
            if brace_start != -1:
                # Count braces to find the matching closing brace
                brace_count = 0
                brace_end = brace_start
                for i, char in enumerate(docstring[brace_start:], brace_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            brace_end = i
                            break
                
                if brace_count == 0:  # Found matching closing brace
                    try:
                        json_str = docstring[brace_start:brace_end + 1]
                        schema_data = json.loads(json_str)
                        schema_info.update(schema_data)
                    except json.JSONDecodeError:
                        pass
        
        # Look for parameter descriptions in docstring
        # Format: @param param_name: description
        param_pattern = r'@param\s+(\w+):\s*(.+?)(?=@|\Z)'
        param_matches = re.finditer(param_pattern, docstring, re.DOTALL)
        
        param_descriptions = {}
        for match in param_matches:
            param_name = match.group(1).strip()
            description = match.group(2).strip()
            param_descriptions[param_name] = description
        
        if param_descriptions:
            schema_info['param_descriptions'] = param_descriptions
        
        return schema_info

    def _get_type_from_annotation(self, annotation) -> str:
        """Convert Python type annotation to JSON schema type"""
        if annotation == inspect.Parameter.empty:
            return "string"
        
        # Handle basic types
        if annotation == int:
            return "integer"
        elif annotation == float:
            return "number"
        elif annotation == bool:
            return "boolean"
        elif annotation == list:
            return "array"
        elif annotation == dict:
            return "object"
        elif annotation == str:
            return "string"
        
        # Handle Union types (e.g., Optional[str])
        if hasattr(annotation, '__origin__'):
            if annotation.__origin__ is Union:
                # For Optional types, get the non-None type
                non_none_types = [arg for arg in annotation.__args__ if arg is not type(None)]
                if non_none_types:
                    return self._get_type_from_annotation(non_none_types[0])
            elif annotation.__origin__ is list:
                return "array"
            elif annotation.__origin__ is dict:
                return "object"
        
        return "string"  # Default fallback

    def to_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling schema"""
        # Get the execute method signature
        sig = inspect.signature(self.execute)
        
        # Parse schema information from docstring
        schema_info = self._parse_docstring_schema()
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "kwargs"):
                continue
            
            # Get type from annotation
            param_type = self._get_type_from_annotation(param.annotation)
            
            # Get description from schema info or use default
            param_descriptions = schema_info.get('param_descriptions', {})
            description = param_descriptions.get(param_name, f"The {param_name} parameter")
            
            # Build property schema
            property_schema = {
                "type": param_type,
                "description": description
            }
            
            # Check for additional schema properties in schema_info
            param_schema_key = f"{param_name}_schema"
            if param_schema_key in schema_info:
                additional_schema = schema_info[param_schema_key]
                # Merge additional properties, but preserve type and description if not overridden
                for key, value in additional_schema.items():
                    if key not in property_schema or key not in ['type', 'description']:
                        property_schema[key] = value
            
            properties[param_name] = property_schema
            
            # Check if parameter is required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # Allow custom schema override
        if 'custom_schema' in schema_info:
            custom_schema = schema_info['custom_schema']
            if 'properties' in custom_schema:
                properties.update(custom_schema['properties'])
            if 'required' in custom_schema:
                required = custom_schema['required']
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }