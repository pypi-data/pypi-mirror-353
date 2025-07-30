# AgentSteam

A fast framework for building Docker-wrapped AI Agents that can connect to go-backend's MCP system.

## Features

- 🤖 **Multi-LLM Support**: Easy adapter system for different LLM providers (Claude, GPT, Gemini, etc.)
- 🔧 **Local Tools**: Simple decorator-based tool system for custom functionality  
- 🌐 **MCP Client**: Connect to go-backend and other MCP servers seamlessly
- 📦 **Docker Ready**: One-command Docker packaging for scenarios
- 📝 **Rich Logging**: Comprehensive logs and outputs for debugging
- ⚡ **Fast Setup**: Get an agent running in minutes

## Quick Start

### Installation

```bash
pip install agent-steam
```

### Basic Usage

1. **Create an agent**:

```python
from agent_steam import AgentSteam, LocalTool

# Define custom tools
@AgentSteam.Tool
class FileReaderTool(LocalTool):
    name = "read_file"
    description = "Read contents of a file"
    
    def execute(self, file_path: str) -> str:
        with open(file_path, 'r') as f:
            return f.read()

# Create agent with system prompt
agent = AgentSteam(
    system_prompt="You are a helpful file processing assistant.",
    llm_provider="claude"  # Set via env: AGENT_STEAM_LLM_PROVIDER
)

# Run the agent
result = agent.run()
```

2. **Package as Docker**:

```bash
agent-steam package
```

3. **Connect to go-backend MCP**:

Set environment variables:
```bash
export MCP_SERVER_URL=http://localhost:8080
export MCP_AUTH_TOKEN=your_token
export AGENT_STEAM_LLM_PROVIDER=claude
export ANTHROPIC_API_KEY=your_key
```

## Architecture

### LLM Adapters
Each LLM has an adapter that handles:
- Message format conversion
- Tool call parsing  
- MCP call parsing
- Response formatting

### Tool System
- **Local Tools**: Python functions with `@AgentSteam.Tool` decorator
- **Predefined Tools**: Built-in tools (Read, Write, Edit, etc.)
- **MCP Tools**: Remote tools from MCP servers

### Input/Output Management
- Input: Read from mounted Docker volumes and environment variables
- Output: Write to `/logs` and `/outputs` directories
- Automatic JSON parsing and file handling

## Development

```bash
git clone <repo>
cd agent-steam
pip install -e ".[dev]"
pytest
```

## License

MIT