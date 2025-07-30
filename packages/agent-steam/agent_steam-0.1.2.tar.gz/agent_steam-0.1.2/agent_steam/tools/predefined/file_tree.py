"""
File tree utilities for directory traversal with .gitignore support.
"""
from typing import Dict, List, Set, Optional, Any, Callable
import os
import fnmatch
import re


class FileTreeBuilder:
    """
    A utility class for building file trees with support for .gitignore patterns.
    This provides a centralized implementation for directory traversal used by
    various tools like LS, Grep, and Glob.
    """
    
    def __init__(self):
        self.gitignore_patterns = {}  # Cache of gitignore patterns by directory
        
    def _parse_gitignore(self, directory: str) -> List[str]:
        """Parse the .gitignore file in the given directory."""
        patterns = []
        gitignore_path = os.path.join(directory, '.gitignore')
        
        if os.path.exists(gitignore_path) and os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            # Handle negated patterns
                            if line.startswith('!'):
                                # Negated patterns are not implemented yet
                                continue
                            # Handle directory-specific patterns
                            patterns.append(line)
            except Exception:
                # If there's an error reading the file, just continue without patterns
                pass
                
        return patterns
        
    def _is_ignored(self, path: str, item: str, additional_ignore: Optional[List[str]] = None) -> bool:
        """
        Check if an item should be ignored based on .gitignore patterns.
        
        Args:
            path: The directory path containing the item
            item: The name of the file or directory
            additional_ignore: Additional ignore patterns to apply
            
        Returns:
            True if the item should be ignored, False otherwise
        """
        # Skip hidden files (files starting with '.')
        if item.startswith('.'):
            return True
            
        # Check additional ignore patterns first
        if additional_ignore:
            for pattern in additional_ignore:
                if fnmatch.fnmatch(item, pattern):
                    return True
        
        # Check if we need to load gitignore patterns for this directory
        if path not in self.gitignore_patterns:
            self.gitignore_patterns[path] = self._parse_gitignore(path)
            
        # Check gitignore patterns
        patterns = self.gitignore_patterns[path]
        for pattern in patterns:
            # Convert gitignore pattern to fnmatch pattern
            if pattern.endswith('/'):
                # Pattern targets directories only
                if os.path.isdir(os.path.join(path, item)):
                    if fnmatch.fnmatch(item, pattern[:-1]):
                        return True
            else:
                # Pattern targets both files and directories
                if fnmatch.fnmatch(item, pattern):
                    return True
                
        return False
    
    def build_tree(self, path: str, ignore: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Build a tree representation of the directory structure.
        
        Args:
            path: The root directory to build the tree from
            ignore: Optional list of glob patterns to ignore
            
        Returns:
            A dictionary representing the tree structure, where keys are file/directory names
            and values are either None for files or another dictionary for directories.
        """
        result_tree = {}
        
        def _build_tree_recursive(current_path: str, tree_node: Dict[str, Any]):
            """Recursively build the directory tree."""
            try:
                # List all items in the directory
                for item in sorted(os.listdir(current_path)):
                    if self._is_ignored(current_path, item, ignore):
                        continue
                        
                    item_path = os.path.join(current_path, item)
                    
                    if os.path.isdir(item_path):
                        # Create a new node for subdirectory
                        tree_node[item] = {}
                        # Recursively process the subdirectory
                        _build_tree_recursive(item_path, tree_node[item])
                    else:
                        # Add file to current node (value is None for files)
                        tree_node[item] = None
                        
            except PermissionError:
                tree_node["__error__"] = f"Permission denied to access: {current_path}"
            except Exception as e:
                tree_node["__error__"] = f"Error processing directory: {str(e)}"
                
        _build_tree_recursive(path, result_tree)
        return result_tree
        
    def collect_files(self, path: str, filter_func: Optional[Callable[[str], bool]] = None, 
                    ignore: Optional[List[str]] = None) -> List[str]:
        """
        Collect all files in the directory tree that pass the filter function.
        
        Args:
            path: The root directory to search from
            filter_func: Optional function to filter files (takes file path, returns boolean)
            ignore: Optional list of glob patterns to ignore
            
        Returns:
            A list of absolute file paths
        """
        files = []
        
        def _traverse_recursive(current_path: str):
            """Recursively collect files."""
            try:
                for item in os.listdir(current_path):
                    if self._is_ignored(current_path, item, ignore):
                        continue
                        
                    item_path = os.path.join(current_path, item)
                    
                    if os.path.isdir(item_path):
                        _traverse_recursive(item_path)
                    elif os.path.isfile(item_path):
                        if filter_func is None or filter_func(item_path):
                            files.append(os.path.abspath(item_path))
                            
            except PermissionError:
                # Skip directories we don't have permission to access
                pass
            except Exception:
                # Skip directories with other errors
                pass
                
        _traverse_recursive(path)
        return files