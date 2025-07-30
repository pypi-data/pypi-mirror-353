from pathlib import Path
from typing import Any
from ..base import LocalTool


class ReadTool(LocalTool):
    """Tool for reading content from files"""
    
    name = "read"
    description = "Read content from a file. Supports pagination for large files."
    
    async def execute(self, file_path: str, offset: int = 1, limit: int = 2000) -> str:
        """Read file content with optional pagination
        
        @param file_path: Absolute path to the file you want to read
        @param offset: Starting line number for reading (1-based index, defaults to 1)
        @param limit: Maximum number of lines to read (defaults to 2000)
        
        @schema: {
            "file_path_schema": {
                "type": "string",
                "pattern": "^/.*",
                "examples": ["/home/user/document.txt", "/var/log/app.log"]
            },
            "offset_schema": {
                "type": "integer",
                "minimum": 1,
                "default": 1
            },
            "limit_schema": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10000,
                "default": 2000
            }
        }
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File '{file_path}' does not exist"
            
            if not path.is_file():
                return f"Error: '{file_path}' is not a file"
            
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    content = lines
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return f"Error: Unable to decode file '{file_path}' with supported encodings"
            
            # Apply pagination
            start_idx = offset - 1  # Convert to 0-based index
            end_idx = start_idx + limit
            
            selected_lines = content[start_idx:end_idx]
            
            # Add line numbers
            result_lines = []
            for i, line in enumerate(selected_lines, start=offset):
                result_lines.append(f"{i:6d}\t{line.rstrip()}")
            
            result = "\n".join(result_lines)
            
            # Add metadata
            total_lines = len(content)
            if total_lines > limit and end_idx < total_lines:
                result += f"\n\n... File has {total_lines} total lines, showing lines {offset}-{min(offset + limit - 1, total_lines)}"
            
            return result
            
        except Exception as e:
            return f"Error reading file: {e}"