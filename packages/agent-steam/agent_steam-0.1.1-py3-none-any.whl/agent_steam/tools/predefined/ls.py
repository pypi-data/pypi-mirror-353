from typing import Dict, Any, List, Optional
import os
from ..base import LocalTool
from .file_tree import FileTreeBuilder

class LSTool(LocalTool):
    """Tool for listing files and directories"""
    name: str = "ls"
    description: str = """Lists files and directories in a given path. The path parameter must be an absolute path, not a relative path. You should generally prefer the Glob and Grep tools, if you know which directories to search. Note: This tool automatically skips hidden files (files starting with '.') and will only return a maximum of 200 results."""
    
    async def execute(self, path: str, ignore: Optional[List[str]] = None) -> Dict[str, Any]:
        """Implement the directory listing functionality with recursive traversal"""
        # Create file tree builder with gitignore support
        tree_builder = FileTreeBuilder()
        
        try:
            # Ensure the path exists and is a directory
            if not os.path.exists(path):
                raise FileNotFoundError(f"Path does not exist: {path}")
            if not os.path.isdir(path):
                raise NotADirectoryError(f"Path is not a directory: {path}")
            
            # Build the tree using our FileTreeBuilder
            result_tree = tree_builder.build_tree(path, ignore)
            
            # Format the output to get a flat list of all directories and files
            all_directories = []
            all_files = []
            
            def collect_items(current_path, current_node):
                """Collect all files and directories from the tree"""
                for item, subtree in current_node.items():
                    if item == "__error__":
                        continue
                        
                    item_path = os.path.join(current_path, item)
                    
                    if subtree is None:  # It's a file
                        all_files.append(item_path)
                    else:  # It's a directory
                        all_directories.append(item_path)
                        collect_items(item_path, subtree)
            
            # Start collecting items from the root
            collect_items(path, result_tree)
            
            # Limit results to 200 items
            sorted_directories = sorted(all_directories)
            sorted_files = sorted(all_files)
            
            # Calculate total result count
            total_count = len(sorted_directories) + len(sorted_files)
            max_results = 200
            
            # Truncate results if they exceed the limit
            if total_count > max_results:
                # Determine how many of each type to include
                dirs_to_include = min(len(sorted_directories), max_results // 2)
                files_to_include = max_results - dirs_to_include
                
                sorted_directories = sorted_directories[:dirs_to_include]
                sorted_files = sorted_files[:files_to_include]
            
            # Return both the tree structure and flat lists
            return {
                "tree": result_tree,
                "directories": sorted_directories,
                "files": sorted_files,
                "truncated": total_count > max_results,
                "total_count": total_count
            }
            
        except FileNotFoundError as e:
            return {"error": f"Path not found: {str(e)}"}
        except PermissionError:
            return {"error": f"Permission denied to access: {path}"}
        except Exception as e:
            return {"error": f"Error listing directory: {str(e)}"}