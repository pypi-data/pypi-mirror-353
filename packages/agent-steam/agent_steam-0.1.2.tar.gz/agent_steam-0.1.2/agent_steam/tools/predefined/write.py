from pathlib import Path
from typing import Any
from ..base import LocalTool


class WriteTool(LocalTool):
    """Tool for writing content to files"""
    
    name = "write"
    description = "Write content to a file. Creates directories if they don't exist."
    
    async def execute(self, file_path: str, content: str) -> str:
        """Write content to a file"""
        try:
            path = Path(file_path)
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote {len(content)} characters to '{file_path}'"
            
        except Exception as e:
            return f"Error writing file: {e}"