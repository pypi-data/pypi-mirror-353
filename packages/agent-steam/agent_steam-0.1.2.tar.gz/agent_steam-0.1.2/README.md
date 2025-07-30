# AgentSteam 🤖

A fast and powerful framework for building Docker-wrapped AI Agents with multi-LLM support, local tools, and MCP integration.

## ✨ Features

- 🤖 **Multi-LLM Support**: Easy adapter system for Claude, GPT, Gemini, and more
- 🔧 **Local Tools**: Simple decorator-based tool system for custom functionality  
- 🌐 **MCP Client**: Connect to go-backend and other MCP servers seamlessly
- 📦 **Docker Ready**: One-command PyInstaller-based packaging for production
- 📝 **Rich Logging**: Comprehensive logs and outputs for debugging
- ⚡ **Fast Setup**: Get an agent running in minutes
- 🎯 **Flexible Entry Points**: Support for custom entrypoint functions
- 🔄 **Pre/Post Processing**: Built-in hooks for input/output processing
- 🌍 **Global Variables**: Share data between tools and components

## 🚀 Quick Start

### Installation

```bash
pip install agent-steam
```

### Basic Agent

Create a simple agent with custom tools:

```python
# agent.py
import asyncio
from agent_steam import AgentSteam, LocalTool

@AgentSteam.Tool
class CalculatorTool(LocalTool):
    name = "calculator"
    description = "Perform basic mathematical calculations"
    
    async def execute(self, expression: str) -> str:
        try:
            result = eval(expression)  # Use safely in production
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

@AgentSteam.entrypoint
async def main():
    agent = AgentSteam(
        system_prompt="You are a helpful calculator assistant."
    )
    return await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Package as Docker Container

```bash
# Package the agent
python -m agent_steam package --source-dir . --agent-name my-agent

# Build Docker container  
cd docker-build
docker build -t my-agent .

# Run the agent
docker run -v ./input:/input -v ./outputs:/outputs my-agent my-agent-cli run
```

## 📚 Core Concepts

### 1. AgentSteam Class Decorators

AgentSteam provides several class-level decorators for different purposes:

#### `@AgentSteam.Tool` - Custom Tools
Register custom tools that the agent can use:

```python
@AgentSteam.Tool
class FileProcessorTool(LocalTool):
    name = "process_file"
    description = "Process a file and return analysis"
    
    async def execute(self, file_path: str, operation: str = "analyze") -> str:
        # Your tool logic here
        with open(file_path, 'r') as f:
            content = f.read()
        
        if operation == "analyze":
            return f"File contains {len(content)} characters"
        elif operation == "summary":
            return f"Summary of {file_path}: {content[:100]}..."
```

#### `@AgentSteam.entrypoint` - Docker Entry Point
Mark a function as the main entry point for Docker containers:

```python
@AgentSteam.entrypoint
async def main():
    # This function will be called when the Docker container runs
    agent = AgentSteam(system_prompt="Your prompt here")
    return await agent.run()
```

#### `@AgentSteam.preProcess` - Input Processing
Process input data before the agent runs:

```python
@AgentSteam.preProcess
def preprocess_input(input_dir: str) -> str:
    """Process input folder and return initial user message"""
    input_path = Path(input_dir)
    
    # Find and process input files
    files = list(input_path.glob("*.txt"))
    if files:
        content = files[0].read_text()
        return f"Please analyze this content: {content}"
    
    return "No input files found, please provide data."
```

#### `@AgentSteam.postProcess` - Output Processing
Process or export outputs after the agent completes:

```python
@AgentSteam.postProcess
def postprocess_output(outputs_dir: str) -> None:
    """Export additional outputs to folder"""
    outputs_path = Path(outputs_dir)
    
    # Create summary report
    summary_file = outputs_path / "analysis_summary.txt"
    with open(summary_file, "w") as f:
        f.write("Analysis completed successfully\\n")
        f.write(f"Global variables: {AgentSteam._global_variables}\\n")
```

### 2. Global Variables

Share data between tools and components:

```python
# Set global variables
AgentSteam.GlobalVariable(
    api_key="your_key_here",
    config={"model": "advanced", "threshold": 0.8}
)

# Update individual variables
AgentSteam.setGlobalVariable("processing_mode", "batch")

# Access in tools
@AgentSteam.Tool
class ConfigurableTool(LocalTool):
    async def execute(self, data: str) -> str:
        api_key = AgentSteam.getGlobalVariable("api_key", "default")
        config = AgentSteam.getGlobalVariable("config", {})
        # Use variables in your logic
        return f"Processed with config: {config}"
```

### 3. Predefined Tools

AgentSteam includes built-in tools. You can select which ones to include:

```python
agent = AgentSteam(
    system_prompt="Your prompt",
    predefined_tools=["read", "write", "bash", "edit"]  # Only these tools
)
```

Available predefined tools:
- `read` - Read file contents
- `write` - Write files
- `edit` - Edit files
- `bash` - Execute bash commands  
- `ls` - List directory contents
- `glob` - Find files by pattern
- `grep` - Search file contents
- `web_fetch` - Fetch web content
- `duckduckgo_search` - Web search
- `ask_for_clarification` - Ask user for input
- `summary` - Summarize content
- `file_tree` - Show directory structure

### 4. Local Tool Development

Create custom tools by extending `LocalTool`:

```python
@AgentSteam.Tool
class DatabaseTool(LocalTool):
    name = "db_query"
    description = "Query the database for information"
    
    async def execute(self, query: str, table: str = "users") -> str:
        """
        Execute a database query
        
        @param query: SQL query to execute
        @param table: Target table name
        """
        # Access logger if needed
        if self.logger:
            self.logger.info(f"Executing query on {table}: {query}")
        
        # Your database logic here
        # result = execute_query(query, table)
        
        return f"Query executed on {table}: {query}"
```

## 🐳 Docker Packaging

### Packaging Command

```bash
python -m agent_steam package [OPTIONS]
```

**Options:**
- `--source-dir` - Directory containing agent code (default: `.`)
- `--output-dir` - Output directory for package (default: `./docker-build`)
- `--agent-name` - Name for the agent executable (default: `my-agent`)
- `--base-image` - Docker base image (default: `ubuntu:22.04`)
- `--additional-packages` - Extra Python packages to include

### Example Packaging

```bash
# Basic packaging
python -m agent_steam package

# Advanced packaging
python -m agent_steam package \\
  --source-dir ./my-agent \\
  --output-dir ./packaged-agent \\
  --agent-name data-processor \\
  --additional-packages pandas numpy requests
```

### Generated Structure

```
packaged-agent/
├── dist/data-processor/      # PyInstaller binary
│   ├── data-processor        # Main executable
│   └── _internal/           # Dependencies
├── Dockerfile               # Container definition
├── docker-compose.yml      # Easy deployment
├── data-processor.spec     # PyInstaller spec
└── build-requirements.txt  # Build dependencies
```

### Docker Commands

```bash
# Build container
cd packaged-agent
docker build -t data-processor .

# Run with help
docker run data-processor

# Run agent with mounted directories
docker run \\
  -v ./input:/input \\
  -v ./outputs:/outputs \\
  -v ./logs:/logs \\
  data-processor data-processor-cli run

# Use docker-compose
docker-compose up
```

## 🔧 Configuration

### Environment Variables

```bash
# LLM Configuration
export AGENT_STEAM_LLM_PROVIDER=claude  # claude, gpt, gemini
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here

# MCP Configuration (optional)
export MCP_SERVER_URL=http://localhost:8080
export MCP_AUTH_TOKEN=your_token_here

# Agent Configuration
export SYSTEM_PROMPT="Custom system prompt"
export AGENT_STEAM_ROOT_DIR=/custom/root  # Change default paths
```

### Directory Structure

Default directory structure in containers:
```
/input/          # Input files (read-only)
/outputs/        # Agent outputs
/logs/           # Log files
```

You can customize paths when creating the agent:

```python
agent = AgentSteam(
    system_prompt="Your prompt",
    input_dir="/custom/input",
    output_dir="/custom/outputs", 
    logs_dir="/custom/logs",
    root_dir="/app"  # Changes default root for all paths
)
```

## 📖 Complete Examples

### Simple Calculator Agent

```python
# examples/simple-agent/agent.py
import asyncio
from agent_steam import AgentSteam, LocalTool

@AgentSteam.Tool
class CalculatorTool(LocalTool):
    name = "calculator"
    description = "Perform mathematical calculations"
    
    async def execute(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

@AgentSteam.entrypoint
async def main():
    agent = AgentSteam(
        system_prompt="You are a helpful calculator. Use the calculator tool for math."
    )
    return await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Data Processing Agent

```python
# examples/advanced-agent/agent.py
import json
from pathlib import Path
from agent_steam import AgentSteam, LocalTool

@AgentSteam.Tool
class DataAnalyzer(LocalTool):
    name = "analyze_data"
    description = "Analyze data using global configuration"
    
    async def execute(self, data: str) -> str:
        # Use logger
        if self.logger:
            self.logger.info(f"Analyzing data: {data[:50]}...")
        
        # Get global variables
        config = AgentSteam.getGlobalVariable("analysis_config", {})
        
        # Perform analysis
        result = f"Analysis completed with config: {config}"
        return result

@AgentSteam.preProcess
def preprocess_input(input_dir: str) -> str:
    """Process input files and return initial message"""
    input_path = Path(input_dir)
    
    json_files = list(input_path.glob("*.json"))
    if json_files:
        with open(json_files[0]) as f:
            data = json.load(f)
        return f"Please analyze this data: {json.dumps(data, indent=2)}"
    
    return "No JSON files found for analysis."

@AgentSteam.postProcess
def postprocess_output(outputs_dir: str) -> None:
    """Create summary report"""
    outputs_path = Path(outputs_dir)
    
    summary_file = outputs_path / "analysis_summary.txt"
    with open(summary_file, "w") as f:
        f.write("Data analysis completed\\n")
        f.write(f"Configuration used: {AgentSteam._global_variables}\\n")

@AgentSteam.entrypoint
async def main():
    # Set global configuration
    AgentSteam.GlobalVariable(
        analysis_config={
            "model": "advanced",
            "threshold": 0.8,
            "output_format": "detailed"
        }
    )
    
    # Create agent with selected tools
    agent = AgentSteam(
        system_prompt="You are a data analysis expert. Use the analyze_data tool.",
        predefined_tools=["read", "write"]  # Only basic file operations
    )
    
    return await agent.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 🔗 MCP Integration

Connect to MCP servers (like go-backend) for remote tools:

```python
# Environment setup
export MCP_SERVER_URL=http://localhost:8080
export MCP_AUTH_TOKEN=your_token

# Agent automatically connects to MCP server
agent = AgentSteam(
    system_prompt="You have access to both local and remote MCP tools.",
    mcp_server_url="http://localhost:8080",  # Optional: override env
    mcp_auth_token="your_token"             # Optional: override env
)
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone <repository>
cd agent-steam
pip install -e ".[dev]"
```

### Project Structure

```
agent_steam/
├── __init__.py
├── core.py              # Main AgentSteam class
├── cli.py               # Command line interface
├── adapters/            # LLM adapters
│   ├── base.py         # Base adapter interface
│   ├── claude.py       # Claude integration
│   └── registry.py     # Adapter registry
├── tools/              # Tool system
│   ├── base.py         # Base tool classes
│   ├── registry.py     # Tool registry
│   └── predefined/     # Built-in tools
├── mcp/                # MCP client
├── io/                 # Input/output management
├── docker/             # Docker packaging
└── utils/              # Utilities
```

### Running Tests

```bash
pytest tests/
```

## 📄 License

MIT License - see LICENSE file for details.

---

**AgentSteam** - Build powerful AI agents, fast. 🚀