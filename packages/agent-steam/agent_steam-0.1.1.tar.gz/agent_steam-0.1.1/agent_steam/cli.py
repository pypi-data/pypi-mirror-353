import click
import asyncio
import os
from pathlib import Path
from .core import AgentSteam
from .docker.packager import DockerPackager


@click.group()
def main():
    """AgentSteam - Fast framework for building Docker-wrapped AI Agents"""
    pass


@main.command()
@click.option('--system-prompt', '-s', help='System prompt for the agent')
@click.option('--llm-provider', '-l', default='claude', help='LLM provider (claude, gpt, etc.)')
@click.option('--input-dir', '-i', default='/input', help='Input directory path')
@click.option('--output-dir', '-o', default='/outputs', help='Output directory path') 
@click.option('--logs-dir', default='/logs', help='Logs directory path')
def run(system_prompt, llm_provider, input_dir, output_dir, logs_dir):
    """Run the agent"""
    
    # Get system prompt from env if not provided
    if not system_prompt:
        system_prompt = os.getenv('SYSTEM_PROMPT', 'You are a helpful AI assistant.')
    
    async def _run():
        agent = AgentSteam(
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            input_dir=input_dir,
            output_dir=output_dir,
            logs_dir=logs_dir
        )
        
        result = await agent.run()
        
        if result.get('success'):
            click.echo("Agent completed successfully!")
        else:
            click.echo(f"Agent failed: {result.get('error')}")
            exit(1)
    
    asyncio.run(_run())


@main.command()
@click.option('--source-dir', '-s', default='.', help='Source directory containing agent code')
@click.option('--output-dir', '-o', default='./docker-build', help='Output directory for Docker files')
@click.option('--base-image', default='python:3.9-slim', help='Base Docker image')
@click.option('--agent-name', default='my-agent', help='Name for the agent')
@click.option('--additional-packages', multiple=True, help='Additional Python packages to include')
def package(source_dir, output_dir, base_image, agent_name, additional_packages):
    """Package agent as Docker container with CLI interface"""
    
    packager = DockerPackager(
        output_dir=Path(output_dir),
        base_image=base_image,
        agent_name=agent_name
    )
    
    try:
        packager.package_agent(
            source_dir=Path(source_dir),
            additional_packages=list(additional_packages) if additional_packages else None
        )
        click.echo("✅ Agent packaged successfully as CLI tool!")
    except Exception as e:
        click.echo(f"❌ Packaging failed: {e}")
        exit(1)


@main.command()
def init():
    """Initialize a new agent project"""
    
    # Create basic project structure
    dirs = ['src', 'input', 'outputs', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Create example agent
    example_agent = '''"""
Example AgentSteam agent
"""
import asyncio
from agent_steam import AgentSteam, LocalTool


@AgentSteam.Tool
class ExampleTool(LocalTool):
    name = "example"
    description = "An example tool that returns a greeting"
    
    async def execute(self, name: str = "World") -> str:
        return f"Hello, {name}!"


async def main():
    agent = AgentSteam(
        system_prompt="You are a helpful assistant. Use the example tool to greet users."
    )
    
    result = await agent.run()
    print(f"Agent result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open('src/agent.py', 'w') as f:
        f.write(example_agent)
    
    # Create requirements.txt
    requirements = '''agent-steam
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    # Create .env example
    env_example = '''# LLM Configuration
AGENT_STEAM_LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_anthropic_key_here

# MCP Configuration (optional)
MCP_SERVER_URL=http://localhost:8080
MCP_AUTH_TOKEN=your_token_here

# Agent Configuration
SYSTEM_PROMPT=You are a helpful assistant.
'''
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    
    click.echo("Agent project initialized!")
    click.echo("1. Copy .env.example to .env and fill in your API keys")
    click.echo("2. Edit src/agent.py to customize your agent")
    click.echo("3. Run with: python src/agent.py")


if __name__ == '__main__':
    main()