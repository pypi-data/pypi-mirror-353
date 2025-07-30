from typing import Dict, Any, Optional, List
from ..base import LocalTool


class ExampleCustomSchemaTool(LocalTool):
    """Example tool demonstrating custom schema definition"""
    
    name = "example_custom_schema"
    description = "Example tool showing how to define custom input schemas"
    
    async def execute(self, search_query: str, filters: Optional[Dict[str, Any]] = None, 
                     max_results: int = 10, include_metadata: bool = False) -> Dict[str, Any]:
        """Execute a search with custom schema validation
        
        This tool demonstrates how to define custom input schemas using docstring annotations.
        
        @param search_query: The search term or phrase to look for
        @param filters: Optional filters to apply to the search results
        @param max_results: Maximum number of results to return (1-100)
        @param include_metadata: Whether to include metadata in the response
        
        @schema: {
            "search_query_schema": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500,
                "pattern": "^[\\w\\s\\-.,!?]+$",
                "examples": ["machine learning", "python tutorial", "data analysis"],
                "description": "Search query must be 1-500 characters and contain only letters, numbers, spaces, and basic punctuation"
            },
            "filters_schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["tech", "science", "business", "education"]
                    },
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string", "format": "date"},
                            "end": {"type": "string", "format": "date"}
                        }
                    },
                    "language": {
                        "type": "string",
                        "enum": ["en", "zh", "es", "fr", "de"]
                    }
                },
                "additionalProperties": false
            },
            "max_results_schema": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 10,
                "examples": [5, 10, 25, 50]
            },
            "include_metadata_schema": {
                "type": "boolean",
                "default": false,
                "description": "When true, includes additional metadata like source, author, and publication date"
            }
        }
        """
        # Simulate search execution
        results = {
            "query": search_query,
            "filters_applied": filters or {},
            "results_count": min(max_results, 42),  # Simulated result count
            "results": [
                {"title": f"Result {i+1}", "content": f"Content for {search_query}"}
                for i in range(min(max_results, 5))
            ]
        }
        
        if include_metadata:
            results["metadata"] = {
                "search_time": "0.1s",
                "total_available": 42,
                "source": "example_db"
            }
        
        return results