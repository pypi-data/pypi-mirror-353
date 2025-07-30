from typing import Dict, Any
import os
import datetime
from ..base import LocalTool

class SummaryTool(LocalTool):
    """Tool for summarizing task information and history"""
    name: str = "summary"
    description: str = """Save task summaries and progress reports to agent history.

This tool helps track task completion, requirements analysis, and important findings.
Creates timestamped markdown files in the .agent-history directory for future reference."""
    
    async def execute(self, summary_file_name: str, summary_content: str) -> Dict[str, Any]:
        """
        Saves the task summary to a file in the .agent-history directory.
        
        Args:
            summary_file_name: A concise name for this task summary
            summary_content: Comprehensive summary of the task details
            
        Returns:
            Dict with success status, message, and file path
        """
        try:
            # Validate input parameters
            if not summary_file_name or not isinstance(summary_file_name, str):
                return {
                    "success": False, 
                    "message": f"Invalid summary file name: {summary_file_name}"
                }
                
            if not isinstance(summary_content, str):
                return {
                    "success": False,
                    "message": "Summary content must be a string"
                }
            
            # Create .agent-history directory if it doesn't exist
            history_dir = os.path.join(os.getcwd(), "agent-history")
            os.makedirs(history_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"history-{timestamp}-{summary_file_name}.md"
            file_path = os.path.join(history_dir, file_name)
            
            # Write content to file
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(summary_content)
                
                return {
                    "success": True,
                    "message": f"Task summary successfully saved",
                    "file_path": file_path
                }
                
            except FileNotFoundError:
                return {
                    "success": False,
                    "message": f"Could not create summary file: {file_path}"
                }
            except PermissionError:
                return {
                    "success": False,
                    "message": f"Permission denied for writing to {file_path}"
                }
            except IsADirectoryError:
                return {
                    "success": False,
                    "message": f"Cannot write to {file_path} because it is a directory"
                }
                
        except Exception as e:
            # Catch any unexpected errors
            return {
                "success": False,
                "message": f"Unexpected error saving summary: {str(e)}"
            }