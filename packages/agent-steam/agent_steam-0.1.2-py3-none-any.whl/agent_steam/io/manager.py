import json
import os
from pathlib import Path
from typing import Dict, Any, Union, List


class IOManager:
    """Manages input/output for agents running in Docker containers"""
    
    def __init__(self, input_dir: Path, output_dir: Path, logs_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logs_dir = Path(logs_dir)
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    async def read_input(self) -> str:
        """Read input from various sources"""
        # 1. Try to read from input.json
        input_file = self.input_dir / "input.json"
        if input_file.exists():
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract user input from different possible formats
                if isinstance(data, str):
                    return data
                elif isinstance(data, dict):
                    return (data.get("input") or 
                            data.get("user_input") or 
                            data.get("prompt") or 
                            data.get("message") or 
                            str(data))
                else:
                    return str(data)
            except Exception:
                pass
        
        # 2. Try to read from environment variable
        env_input = os.getenv("AGENT_INPUT")
        if env_input:
            return env_input
        
        # 3. Try to read from input.txt
        input_txt = self.input_dir / "input.txt"
        if input_txt.exists():
            try:
                with open(input_txt, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        # 4. Default message
        return "Please help me complete the task."
    
    async def write_output(self, data: Dict[str, Any]) -> None:
        """Write output to output directory"""
        # Write to output.json
        output_file = self.output_dir / "output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Also write a summary if response exists
        if "response" in data:
            summary_file = self.output_dir / "summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(data["response"])
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get relevant environment variables"""
        env_vars = {}
        
        # LLM configuration
        llm_env_vars = [
            "AGENT_STEAM_LLM_PROVIDER",
            "ANTHROPIC_API_KEY", 
            "OPENAI_API_KEY",
            "GEMINI_API_KEY"
        ]
        
        # MCP configuration  
        mcp_env_vars = [
            "MCP_SERVER_URL",
            "MCP_AUTH_TOKEN"
        ]
        
        # Agent configuration
        agent_env_vars = [
            "AGENT_INPUT",
            "SYSTEM_PROMPT"
        ]
        
        for var in llm_env_vars + mcp_env_vars + agent_env_vars:
            value = os.getenv(var)
            if value:
                env_vars[var] = value
        
        return env_vars
    
    def list_input_files(self) -> List[str]:
        """List all files in input directory"""
        if not self.input_dir.exists():
            return []
        
        files = []
        for item in self.input_dir.iterdir():
            if item.is_file():
                files.append(str(item.relative_to(self.input_dir)))
        
        return sorted(files)