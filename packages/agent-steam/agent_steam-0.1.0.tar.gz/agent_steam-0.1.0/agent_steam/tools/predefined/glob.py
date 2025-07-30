from typing import Dict, Any, List, Optional
import os
import glob
import fnmatch
from pathlib import Path
from ..base import LocalTool
from .file_tree import FileTreeBuilder

class GlobTool(LocalTool):
    """Tool for finding files using glob patterns"""
    name: str = "glob"
    description: str = """Fast file pattern matching tool that works with any codebase size
- Supports glob patterns like "**/*.js" or "src/**/*.ts"
- Returns matching file paths sorted by modification time
- Use this tool when you need to find files by name patterns
- When you are doing an open ended search that may require multiple rounds of globbing and grepping, use the Agent tool instead"""
    
    async def execute(self, pattern: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Implement the glob pattern matching functionality with recursive directory traversal"""
        try:
            # Set default path to current directory if not provided
            search_path = path or os.getcwd()
            
            # Ensure the path exists and is a directory
            if not os.path.exists(search_path):
                raise FileNotFoundError(f"Path does not exist: {search_path}")
            if not os.path.isdir(search_path):
                raise NotADirectoryError(f"Path is not a directory: {search_path}")
            
            # Extract the file pattern from the glob pattern
            # This handles patterns like "**/*.py" -> "*.py"
            file_pattern = os.path.basename(pattern)
            if not file_pattern or file_pattern == "**":
                file_pattern = "*"
                
            # Import FileTreeBuilder
            tree_builder = FileTreeBuilder()
            
            # List to store all matching files
            matches = []
            
            # Handle glob patterns directly if they have special characters
            if "**" in pattern or "*" in pattern or "?" in pattern or "[" in pattern:
                # Use glob.glob with recursive=True for standard glob patterns
                pattern_path = os.path.join(search_path, pattern) if not os.path.isabs(pattern) else pattern
                glob_matches = glob.glob(pattern_path, root_dir=search_path, recursive=True)
                
                # Filter out directories and convert to absolute paths
                absolute_matches = [
                    os.path.abspath(match) for match in glob_matches
                    if os.path.isfile(match)
                ]
                
                matches.extend(absolute_matches)
            else:
                # For simple patterns, use FileTreeBuilder
                
                # Define a filter function for files matching the pattern
                def file_filter(file_path):
                    filename = os.path.basename(file_path)
                    return fnmatch.fnmatch(filename, file_pattern)
                
                # Collect matching files
                matches = tree_builder.collect_files(search_path, file_filter)
            
            # Remove duplicates and sort by modification time (newest first)
            unique_matches = list(set(matches))
            unique_matches.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return {
                "matches": unique_matches
            }
            
        except FileNotFoundError as e:
            return {"error": f"Path not found: {str(e)}"}
        except PermissionError:
            return {"error": f"Permission denied to access: {search_path}"}
        except Exception as e:
            return {"error": f"Error during glob search: {str(e)}"}