from pathlib import Path
from typing import Any
from ..base import LocalTool


class EditTool(LocalTool):
    """Tool for editing files with find and replace"""
    
    name = "edit"
    description = "Edit a file by replacing old text with new text. Uses exact string matching."
    
    async def execute(self, file_path: str, old_text: str, new_text: str) -> str:
        """Edit file by replacing old_text with new_text"""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File '{file_path}' does not exist"
            
            # Read current content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_text exists
            if old_text not in content:
                return f"Error: Text to replace not found in file '{file_path}'"
            
            # Count occurrences
            count = content.count(old_text)
            if count > 1:
                return f"Error: Found {count} occurrences of the text. Please be more specific to avoid unintended replacements."
            
            # Replace the text
            new_content = content.replace(old_text, new_text)
            
            # Write back to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return f"Successfully replaced text in '{file_path}'. Changed {len(old_text)} characters to {len(new_text)} characters."
            
        except Exception as e:
            return f"Error editing file: {e}"