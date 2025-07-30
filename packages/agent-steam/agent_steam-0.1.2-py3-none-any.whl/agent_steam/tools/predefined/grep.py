from typing import Dict, Any, List, Optional
import os
import re
import subprocess
import fnmatch
from ..base import LocalTool
from .file_tree import FileTreeBuilder

class GrepTool(LocalTool):
    """Tool for searching file contents"""
    name: str = "grep"
    description: str = """Fast content search tool that works with any codebase size
- Searches file contents using regular expressions
- Supports full regex syntax (eg. "log.*Error", "function\\s+\\w+", etc.)
- Filter files by pattern with the include parameter (eg. "*.js", "*.{ts,tsx}")
- Returns matching file paths sorted by modification time
- Use this tool when you need to find files containing specific patterns
- When you are doing an open ended search that may require multiple rounds of globbing and grepping, use the Agent tool instead"""
    
    async def execute(self, pattern: str, path: Optional[str] = None, include: Optional[str] = None) -> Dict[str, Any]:
        """Implement the grep search functionality using system grep command for better performance
        with fallback to pure Python implementation if grep command fails"""
        try:
            # Set default path to current directory if not provided
            search_path = path or os.getcwd()
            
            # Ensure the path exists and is a directory
            if not os.path.exists(search_path):
                raise FileNotFoundError(f"Path does not exist: {search_path}")
            if not os.path.isdir(search_path):
                raise NotADirectoryError(f"Path is not a directory: {search_path}")
            
            # Validate regex pattern
            try:
                compiled_regex = re.compile(pattern)
            except re.error as e:
                return {"error": f"Invalid regular expression pattern: {str(e)}"}
            
            matches = []
            use_system_grep = True
            
            try:
                # Construct grep command
                cmd = ["grep", "-n", "-r", "-P"]  # -n for line numbers, -r for recursive, -P for perl regex
                
                # Add include pattern if specified
                if include:
                    cmd.extend(["--include", include])
                
                # Add pattern and search path
                cmd.extend([pattern, search_path])
                
                # Execute command
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    errors='replace',
                    timeout=30  # 30 second timeout
                )
                
                if process.returncode not in [0, 1]:  # 0=matches found, 1=no matches
                    # Grep command failed, fall back to Python implementation
                    use_system_grep = False
                else:
                    # Parse output from system grep
                    for line in process.stdout.splitlines():
                        if ":" not in line:
                            continue
                            
                        # Output format is: file_path:line_number:content
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            file_path, line_number, content = parts
                            try:
                                matches.append({
                                    "file": os.path.abspath(file_path),
                                    "line_number": int(line_number),
                                    "line": content
                                })
                            except ValueError:
                                # Skip if line number can't be parsed
                                continue
            except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
                # Fallback to Python implementation if grep command fails
                use_system_grep = False
            
            # Fallback to Python implementation if system grep failed
            if not use_system_grep:
                # List to store all matches
                matches = []
                
                # Process files based on include pattern
                tree_builder = FileTreeBuilder()
                
                def search_file(file_path):
                    """Search for pattern in a single file"""
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            for i, line in enumerate(f, 1):
                                if compiled_regex.search(line):
                                    matches.append({
                                        "file": os.path.abspath(file_path),
                                        "line_number": i,
                                        "line": line
                                    })
                    except UnicodeDecodeError:
                        # Skip binary files
                        pass
                    except PermissionError:
                        # Skip files we don't have permission to read
                        pass
                    except Exception:
                        # Skip files with other errors
                        pass
                
                # Define a filter function to handle include patterns
                def file_filter(file_path):
                    if not include:
                        return True
                    filename = os.path.basename(file_path)
                    return fnmatch.fnmatch(filename, include)
                
                # Use the file tree builder to collect files
                collected_files = tree_builder.collect_files(search_path, file_filter)
                
                # Process all collected files
                for file_path in collected_files:
                    search_file(file_path)
            
            # Sort matches by modification time (newest files first)
            file_mod_times = {}
            for match in matches:
                file_path = match["file"]
                if file_path not in file_mod_times:
                    try:
                        file_mod_times[file_path] = os.path.getmtime(file_path)
                    except (FileNotFoundError, PermissionError):
                        file_mod_times[file_path] = 0
            
            matches.sort(key=lambda x: (file_mod_times.get(x["file"], 0), x["line_number"]), reverse=True)
            
            # Limit matches to avoid excessive output
            max_matches = 100
            limited_matches = matches[:max_matches]
            
            return {
                "matches": limited_matches
            }
            
        except FileNotFoundError as e:
            return {"error": f"Path not found: {str(e)}"}
        except PermissionError:
            return {"error": f"Permission denied to access: {search_path}"}
        except Exception as e:
            return {"error": f"Error during grep search: {str(e)}"}