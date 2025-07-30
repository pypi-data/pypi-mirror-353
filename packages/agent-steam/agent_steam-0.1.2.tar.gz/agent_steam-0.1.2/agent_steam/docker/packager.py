import subprocess
import sys
from pathlib import Path
from typing import Optional
from ..core import AgentSteam


class DockerPackager:
    """Package agent as Docker container using PyInstaller"""
    
    def __init__(self, output_dir: Path, base_image: str = "ubuntu:22.04", agent_name: str = "my-agent"):
        self.output_dir = Path(output_dir)
        self.base_image = base_image
        self.agent_name = agent_name
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get entrypoint information from AgentSteam
        self.entrypoint_info = AgentSteam.get_entrypoint_info()
    
    def create_dockerfile(self) -> None:
        """Create Dockerfile for the agent using PyInstaller binary"""
        
        dockerfile_content = f'''FROM {self.base_image}

# Install system dependencies for running the binary
RUN apt-get update && apt-get install -y \\
    && rm -rf /var/lib/apt/lists/*

# Create directories for input/output
RUN mkdir -p /input /outputs /logs

# Copy the PyInstaller packaged binary
COPY dist/{self.agent_name}/ /usr/local/bin/{self.agent_name}/

# Make the main executable accessible in PATH
RUN ln -s /usr/local/bin/{self.agent_name}/{self.agent_name} /usr/local/bin/{self.agent_name}-cli

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command runs the agent
CMD ["{self.agent_name}-cli", "run"]
'''
        
        dockerfile_path = self.output_dir / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
    
    def create_cli_wrapper(self, source_dir: Path) -> Path:
        """Create CLI wrapper script for PyInstaller packaging"""
        
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
            
            cli_content = f'''#!/usr/bin/env python
"""
AgentSteam CLI tool for containerized agent execution
Using decorated entrypoint function: {function_name} from {import_module}
"""
import asyncio
import click
import os
import sys
import json
from pathlib import Path

# Add the agent source directory to path
current_dir = Path(__file__).parent
agent_dir = current_dir / "agent_src"
if agent_dir.exists():
    sys.path.insert(0, str(agent_dir))

# Add agent_steam module to path for PyInstaller packed executable
try:
    import agent_steam
    agent_steam_dir = Path(agent_steam.__file__).parent.parent
    if agent_steam_dir not in [Path(p) for p in sys.path]:
        sys.path.insert(0, str(agent_steam_dir))
except ImportError:
    # If running in PyInstaller environment, try to find agent_steam in _internal
    if hasattr(sys, '_MEIPASS'):
        internal_dir = Path(sys._MEIPASS)
        if internal_dir.exists():
            sys.path.insert(0, str(internal_dir))

@click.group()
def cli():
    """AgentSteam containerized agent CLI"""
    pass

@cli.command()
@click.option('--input-dir', '-i', default='/input', help='Input directory path')
@click.option('--output-dir', '-o', default='/outputs', help='Output directory path')
@click.option('--logs-dir', '-l', default='/logs', help='Logs directory path')
@click.option('--system-prompt', '-s', help='Override system prompt')
@click.option('--llm-provider', default=None, help='Override LLM provider')
def run(input_dir, output_dir, logs_dir, system_prompt, llm_provider):
    """Run the agent"""
    
    # Set environment variables for the agent
    if system_prompt:
        os.environ['SYSTEM_PROMPT'] = system_prompt
    if llm_provider:
        os.environ['AGENT_STEAM_LLM_PROVIDER'] = llm_provider
    
    # Set directory paths
    os.environ['INPUT_DIR'] = input_dir
    os.environ['OUTPUT_DIR'] = output_dir
    os.environ['LOGS_DIR'] = logs_dir
    
    async def _run():
        try:
            from {import_module} import {function_name}
            
            print(f"Starting AgentSteam agent with entrypoint: {function_name}...")
            print(f"Input dir: {{input_dir}}")
            print(f"Output dir: {{output_dir}}")
            print(f"Logs dir: {{logs_dir}}")
            
            # Check if the function is async
            import inspect
            if inspect.iscoroutinefunction({function_name}):
                result = await {function_name}()
            else:
                result = {function_name}()
            
            print("Agent completed successfully.")
            
            # Write success result
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            if result and isinstance(result, dict):
                with open(output_path / "output.json", "w") as f:
                    json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            print(f"Error running agent: {{e}}")
            
            # Write error to output
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            with open(output_path / "output.json", "w") as f:
                json.dump({{"success": False, "error": str(e)}}, f, indent=2)
            
            sys.exit(1)
    
    asyncio.run(_run())

@cli.command()
def info():
    """Show agent information"""
    print("AgentSteam Containerized Agent")
    print(f"Entrypoint: {function_name} from {import_module}")
    print(f"Default input: /input")
    print(f"Default output: /outputs")
    print(f"Default logs: /logs")

if __name__ == "__main__":
    cli()
'''
        else:
            # Fallback to default behavior
            cli_content = '''#!/usr/bin/env python
"""
AgentSteam CLI tool for containerized agent execution
Using default main function
"""
import asyncio
import click
import os
import sys
import json
from pathlib import Path

# Add the agent source directory to path
current_dir = Path(__file__).parent
agent_dir = current_dir / "agent_src"
if agent_dir.exists():
    sys.path.insert(0, str(agent_dir))

# Add agent_steam module to path for PyInstaller packed executable
try:
    import agent_steam
    agent_steam_dir = Path(agent_steam.__file__).parent.parent
    if agent_steam_dir not in [Path(p) for p in sys.path]:
        sys.path.insert(0, str(agent_steam_dir))
except ImportError:
    # If running in PyInstaller environment, try to find agent_steam in _internal
    if hasattr(sys, '_MEIPASS'):
        internal_dir = Path(sys._MEIPASS)
        if internal_dir.exists():
            sys.path.insert(0, str(internal_dir))

@click.group()
def cli():
    """AgentSteam containerized agent CLI"""
    pass

@cli.command()
@click.option('--input-dir', '-i', default='/input', help='Input directory path')
@click.option('--output-dir', '-o', default='/outputs', help='Output directory path')
@click.option('--logs-dir', '-l', default='/logs', help='Logs directory path')
@click.option('--system-prompt', '-s', help='Override system prompt')
@click.option('--llm-provider', default=None, help='Override LLM provider')
def run(input_dir, output_dir, logs_dir, system_prompt, llm_provider):
    """Run the agent"""
    
    # Set environment variables for the agent
    if system_prompt:
        os.environ['SYSTEM_PROMPT'] = system_prompt
    if llm_provider:
        os.environ['AGENT_STEAM_LLM_PROVIDER'] = llm_provider
    
    # Set directory paths
    os.environ['INPUT_DIR'] = input_dir
    os.environ['OUTPUT_DIR'] = output_dir
    os.environ['LOGS_DIR'] = logs_dir
    
    async def _run():
        try:
            from agent import main
            
            print("Starting AgentSteam agent...")
            print(f"Input dir: {input_dir}")
            print(f"Output dir: {output_dir}")
            print(f"Logs dir: {logs_dir}")
            
            result = await main()
            print("Agent completed successfully.")
            
            # Write success result
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            if result and isinstance(result, dict):
                with open(output_path / "output.json", "w") as f:
                    json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            print(f"Error running agent: {e}")
            
            # Write error to output
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            with open(output_path / "output.json", "w") as f:
                json.dump({"success": False, "error": str(e)}, f, indent=2)
            
            sys.exit(1)
    
    asyncio.run(_run())

@cli.command()
def info():
    """Show agent information"""
    print("AgentSteam Containerized Agent")
    print("Entrypoint: main() function from agent module")
    print("Default input: /input")
    print("Default output: /outputs")
    print("Default logs: /logs")

if __name__ == "__main__":
    cli()
'''
        
        cli_path = self.output_dir / f"{self.agent_name}_cli.py"
        with open(cli_path, 'w') as f:
            f.write(cli_content)
        
        return cli_path
    
    def create_pyinstaller_spec(self, cli_script_path: Path, source_dir: Path, additional_packages: Optional[list] = None) -> Path:
        """Create PyInstaller spec file"""
        
        # Build hidden imports list
        hidden_imports = [
            'agent_steam',
            'agent_steam.core',
            'agent_steam.adapters',
            'agent_steam.adapters.claude',
            'agent_steam.tools',
            'agent_steam.tools.predefined',
            'agent_steam.io',
            'agent_steam.mcp',
            'click',
            'asyncio',
            'json',
            'pathlib',
            'os',
            'sys',
        ]
        
        if additional_packages:
            hidden_imports.extend(additional_packages)
        
        # Convert paths to absolute
        cli_script_abs = cli_script_path.absolute()
        source_dir_abs = source_dir.absolute()
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import site
from pathlib import Path

# Find agent_steam package location
import agent_steam
agent_steam_path = Path(agent_steam.__file__).parent

a = Analysis(
    ['{cli_script_abs}'],
    pathex=[],
    binaries=[],
    datas=[
        ('{source_dir_abs}', 'agent_src'),
        (str(agent_steam_path), 'agent_steam'),
    ],
    hiddenimports={hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{self.agent_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{self.agent_name}',
)
'''
        
        spec_path = self.output_dir / f"{self.agent_name}.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        return spec_path
    
    def build_with_pyinstaller(self, spec_path: Path) -> None:
        """Build the agent using PyInstaller"""
        
        print(f"Building agent with PyInstaller using spec: {spec_path}")
        
        # Run PyInstaller
        try:
            result = subprocess.run([
                sys.executable, '-m', 'PyInstaller',
                spec_path.name
            ], cwd=self.output_dir, capture_output=True, text=True, check=True)
            
            print("PyInstaller build completed successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"PyInstaller build failed with exit code {e.returncode}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise
        except FileNotFoundError:
            print("PyInstaller not found. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
            # Retry the build
            result = subprocess.run([
                sys.executable, '-m', 'PyInstaller',
                spec_path.name
            ], cwd=self.output_dir, capture_output=True, text=True, check=True)
            
            print("PyInstaller build completed successfully!")
    
    def create_build_requirements(self, additional_packages: Optional[list] = None) -> None:
        """Create requirements.txt file for building"""
        
        base_requirements = [
            "agent-steam",
            "click",
            "pyinstaller",
        ]
        
        if additional_packages:
            base_requirements.extend(additional_packages)
        
        requirements_content = "\\n".join(base_requirements) + "\\n"
        
        requirements_path = self.output_dir / "build-requirements.txt"
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
    # Override the default command to run the agent
    command: ["{self.agent_name}-cli", "run"]
'''
        
        compose_path = self.output_dir / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write(compose_content)
    
    def package_agent(self, source_dir: Path, additional_packages: Optional[list] = None) -> None:
        """
        Package the complete agent for Docker deployment using PyInstaller.
        
        Args:
            source_dir: Directory containing the agent source code
            additional_packages: Additional Python packages to include in requirements.txt
        """
        print(f"Packaging agent from {source_dir} to {self.output_dir} using PyInstaller")
        
        # Get entrypoint info for reporting
        entrypoint_info = AgentSteam.get_entrypoint_info()
        if entrypoint_info["has_entrypoint"]:
            print(f"Using custom entrypoint: {entrypoint_info['function_name']} from {entrypoint_info['module']}")
        else:
            print("Using default entrypoint: main() function")
        
        # Step 1: Create CLI wrapper script
        print("Creating CLI wrapper script...")
        cli_script_path = self.create_cli_wrapper(source_dir)
        
        # Step 2: Create PyInstaller spec file
        print("Creating PyInstaller spec file...")
        spec_path = self.create_pyinstaller_spec(cli_script_path, source_dir, additional_packages)
        
        # Step 3: Create build requirements
        print("Creating build requirements...")
        self.create_build_requirements(additional_packages)
        
        # Step 4: Build with PyInstaller
        print("Building with PyInstaller...")
        self.build_with_pyinstaller(spec_path)
        
        # Step 5: Create Dockerfile for the binary
        print("Creating Dockerfile...")
        self.create_dockerfile()
        
        # Step 6: Create docker-compose.yml
        print("Creating docker-compose.yml...")
        self.create_docker_compose()
        
        print(f"\n✅ Agent packaged successfully in {self.output_dir}")
        print(f"📦 PyInstaller binary created in: {self.output_dir}/dist/{self.agent_name}/")
        print(f"\nTo build and run the Docker container:")
        print(f"  cd {self.output_dir}")
        print(f"  docker build -t {self.agent_name} .")
        print(f"\nTo test the CLI:")
        print(f"  # Show CLI help:")
        print(f"  docker run {self.agent_name}")
        print(f"  # Run the agent:")
        print(f"  docker run -v ./input:/input -v ./outputs:/outputs {self.agent_name} {self.agent_name}-cli run")
        print(f"  # Get agent info:")
        print(f"  docker run {self.agent_name} {self.agent_name}-cli info")
        print(f"\nOr use docker-compose:")
        print(f"  cd {self.output_dir}")
        print(f"  docker-compose up")