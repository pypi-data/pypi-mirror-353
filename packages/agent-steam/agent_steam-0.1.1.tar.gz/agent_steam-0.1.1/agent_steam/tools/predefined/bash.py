from typing import Dict, Any, Optional, List
import os
import subprocess
import shlex
import logging
import time
import signal
from ..base import LocalTool

class BashTool(LocalTool):
    """Tool for executing bash commands"""
    name: str = "bash"
    description: str = """Execute bash commands in a persistent shell session with optional timeout.

Features:
- Execute bash commands with proper error handling
- Optional timeout configuration (default: 60 seconds)
- Working directory specification
- Environment variable setting
- Safety checks for dangerous commands
- Detailed output including stdout, stderr, exit code, and execution time"""

    # List of potentially dangerous commands that should be blocked
    DANGEROUS_COMMANDS: List[str] = [
        "rm -rf /", "rm -rf /*", "dd if=/dev/random",
        ":(){ :|:& };:", "chmod -R 777 /", "mv /* /dev/null"
    ]
    
    # Network-related commands that might need extra confirmation
    NETWORK_COMMANDS: List[str] = [
        "wget", "curl", "nc", "netcat", "telnet", "ssh", "ftp", "sftp"
    ]
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if the command is potentially dangerous"""
        # Strip comments and whitespace for safer comparison
        clean_command = command.split('#')[0].strip()
        
        # Check against dangerous command patterns
        for dangerous in self.DANGEROUS_COMMANDS:
            if dangerous in clean_command:
                return True
                
        # Look for suspicious patterns like large rm operations
        if "rm -rf" in clean_command and "*" in clean_command:
            return True
            
        return False
    
    def _is_network_command(self, command: str) -> bool:
        """Check if the command is related to network operations"""
        # Get the first word (the actual command)
        cmd = command.strip().split()[0]
        return cmd in self.NETWORK_COMMANDS
    
    async def execute(self, command: str, timeout: Optional[int] = None, 
                     cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute the bash command
        
        @param command: The bash command to execute (e.g., 'ls -la', 'grep pattern file.txt')
        @param timeout: Maximum execution time in seconds (1-300 seconds, default: 60)
        @param cwd: Working directory path for command execution (absolute path)
        @param env: Environment variables as key-value pairs
        
        @schema: {
            "command_schema": {
                "type": "string",
                "minLength": 1,
                "examples": ["ls -la", "grep 'error' /var/log/app.log", "python script.py"]
            },
            "timeout_schema": {
                "type": "integer",
                "minimum": 1,
                "maximum": 300,
                "default": 60
            },
            "cwd_schema": {
                "type": "string",
                "pattern": "^/.*",
                "examples": ["/home/user/project", "/tmp"]
            },
            "env_schema": {
                "type": "object",
                "additionalProperties": {
                    "type": "string"
                },
                "examples": [{"PATH": "/usr/bin:/bin", "HOME": "/home/user"}]
            }
        }
        
        Returns:
            Dictionary with stdout, stderr, exit_code, and execution_time
        """
        # Check for dangerous commands
        if self._is_dangerous_command(command):
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": "Command execution blocked: potentially dangerous command detected",
                "execution_time": 0
            }
            
        # Set default timeout if not provided
        if timeout is None:
            timeout = 60  # Default 60 seconds
            
        # Prepare environment variables
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
            
        # Track execution time
        start_time = time.time()
        
        try:
            # Use subprocess to execute the command
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=process_env
            )
            
            execution_time = time.time() - start_time
            
            return {
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "execution_time": execution_time
            }
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "exit_code": 124,  # Standard timeout exit code
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "execution_time": execution_time
            }
        except FileNotFoundError:
            execution_time = time.time() - start_time
            return {
                "exit_code": 127,  # Command not found exit code
                "stdout": "",
                "stderr": f"Command not found: {command.split()[0]}",
                "execution_time": execution_time
            }
        except PermissionError:
            execution_time = time.time() - start_time
            return {
                "exit_code": 126,  # Permission denied exit code
                "stdout": "",
                "stderr": f"Permission denied: {command}",
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "execution_time": execution_time
            }