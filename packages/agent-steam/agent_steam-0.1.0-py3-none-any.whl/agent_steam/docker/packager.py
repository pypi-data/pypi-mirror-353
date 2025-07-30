from pathlib import Path
from typing import Optional, Dict
from ..core import AgentSteam


class DockerPackager:
    """Package agent as Docker container"""
    
    def __init__(self, output_dir: Path, base_image: str = "python:3.9-slim", agent_name: str = "my-agent"):
        self.output_dir = Path(output_dir)
        self.base_image = base_image
        self.agent_name = agent_name
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get entrypoint information from AgentSteam
        self.entrypoint_info = AgentSteam.get_entrypoint_info()
    
    def create_dockerfile(self) -> None:
        """Create Dockerfile for the agent"""
        
        dockerfile_content = f'''FROM {self.base_image}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY src/ ./src/
COPY entrypoint.py .

# Create directories for input/output
RUN mkdir -p /input /outputs /logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the agent
CMD ["python", "entrypoint.py"]
'''
        
        dockerfile_path = self.output_dir / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
    
    def create_entrypoint(self) -> None:
        """Create entrypoint script that uses the registered @AgentSteam.entrypoint function"""
        
        # Determine which module and function to use
        if self.entrypoint_info["has_entrypoint"]:
            # Use the decorated entrypoint function
            module_name = self.entrypoint_info["module"]
            function_name = self.entrypoint_info["function_name"]
            
            # Strip any package prefix from module name for import
            if module_name.startswith("__main__"):
                # If it's the main module, assume it's in agent.py
                import_module = "agent"
            else:
                # Use the module name as-is, but strip any package prefixes
                import_module = module_name.split(".")[-1] if "." in module_name else module_name
            
            entrypoint_content = f'''#!/usr/bin/env python
"""
Entrypoint script for AgentSteam Docker container
Using decorated entrypoint function: {function_name} from {import_module}
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, '/app/src')

try:
    from {import_module} import {function_name}
    
    async def run_agent():
        """Run the agent using the decorated entrypoint function"""
        print(f"Starting AgentSteam agent with entrypoint: {{function_name}}...")
        
        # Check if the function is async
        import inspect
        if inspect.iscoroutinefunction({function_name}):
            result = await {function_name}()
        else:
            result = {function_name}()
        
        print("Agent completed.")
        return result
    
    if __name__ == "__main__":
        asyncio.run(run_agent())
        
except Exception as e:
    print(f"Error running agent: {{e}}")
    # Write error to output
    output_dir = Path("/outputs")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "output.json", "w") as f:
        import json
        json.dump({{"success": False, "error": str(e)}}, f)
    
    sys.exit(1)
'''
        else:
            # Fallback to default behavior
            entrypoint_content = '''#!/usr/bin/env python
"""
Entrypoint script for AgentSteam Docker container
Using default main function
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, '/app/src')

try:
    from agent import main
    
    async def run_agent():
        """Run the agent"""
        print("Starting AgentSteam agent...")
        await main()
        print("Agent completed.")
    
    if __name__ == "__main__":
        asyncio.run(run_agent())
        
except Exception as e:
    print(f"Error running agent: {e}")
    # Write error to output
    output_dir = Path("/outputs")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "output.json", "w") as f:
        import json
        json.dump({"success": False, "error": str(e)}, f)
    
    sys.exit(1)
'''
        
        entrypoint_path = self.output_dir / "entrypoint.py"
        with open(entrypoint_path, 'w') as f:
            f.write(entrypoint_content)
        
        # Make it executable
        entrypoint_path.chmod(0o755)
    
    def create_requirements(self, additional_packages: Optional[list] = None) -> None:
        """Create requirements.txt file"""
        
        base_requirements = [
            "agent-steam",
        ]
        
        if additional_packages:
            base_requirements.extend(additional_packages)
        
        requirements_content = "\\n".join(base_requirements) + "\\n"
        
        requirements_path = self.output_dir / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
    
    def create_docker_compose(self) -> None:
        """Create docker-compose.yml for easy deployment"""
        
        compose_content = f'''version: '3.8'

services:
  {self.agent_name}:
    build: .
    container_name: {self.agent_name}
    volumes:
      - ./input:/input:ro
      - ./outputs:/outputs
      - ./logs:/logs
    environment:
      - AGENT_STEAM_LLM_PROVIDER=${{AGENT_STEAM_LLM_PROVIDER:-claude}}
      - ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}
      - OPENAI_API_KEY=${{OPENAI_API_KEY}}
      - MCP_SERVER_URL=${{MCP_SERVER_URL}}
      - MCP_AUTH_TOKEN=${{MCP_AUTH_TOKEN}}
      - SYSTEM_PROMPT=${{SYSTEM_PROMPT}}
    restart: "no"
'''
        
        compose_path = self.output_dir / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write(compose_content)
    
    def package_agent(self, source_dir: Path, additional_packages: Optional[list] = None) -> None:
        """
        Package the complete agent for Docker deployment.
        
        Args:
            source_dir: Directory containing the agent source code
            additional_packages: Additional Python packages to include in requirements.txt
        """
        print(f"Packaging agent from {source_dir} to {self.output_dir}")
        
        # Get entrypoint info for reporting
        entrypoint_info = AgentSteam.get_entrypoint_info()
        if entrypoint_info["has_entrypoint"]:
            print(f"Using custom entrypoint: {entrypoint_info['function_name']} from {entrypoint_info['module']}")
        else:
            print("Using default entrypoint: main() function")
        
        # Create all necessary files
        self.create_dockerfile()
        self.create_entrypoint()
        self.create_requirements(additional_packages)
        self.create_docker_compose()
        
        # Copy source code to output directory
        import shutil
        src_output_dir = self.output_dir / "src"
        if src_output_dir.exists():
            shutil.rmtree(src_output_dir)
        shutil.copytree(source_dir, src_output_dir)
        
        print(f"Agent packaged successfully in {self.output_dir}")
        print(f"To build and run:")
        print(f"  cd {self.output_dir}")
        print(f"  docker build -t {self.agent_name} .")
        print(f"  docker run -v ./input:/input -v ./outputs:/outputs {self.agent_name}")
        print(f"Or use docker-compose:")
        print(f"  cd {self.output_dir}")
        print(f"  docker-compose up")