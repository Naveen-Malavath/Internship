# AI Coding Agent

An autonomous AI agent that generates full-stack applications from a single prompt, with self-healing capabilities.

## Features

- 🤖 **Autonomous**: Takes a single prompt and completes complex tasks
- 🔧 **Full-Stack**: Generates frontend, backend, APIs, and configs
- 🔄 **Self-Healing**: Detects and fixes errors automatically
- 🔍 **Smart Search**: Efficient code navigation for large projects
- 🚀 **Multiple LLMs**: Supports OpenAI and Anthropic

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
```

### 3. Run

```bash
# Simple command
python -m src.main run "Create a Python hello world script"

# Full-stack app
python -m src.main run "Create a todo app with React frontend and Express backend"

# Interactive mode
python -m src.main interactive
```

## Usage Examples

### Create a Simple Script
```bash
python -m src.main run "Create a Python script that fetches weather data"
```

### Generate Full-Stack App
```bash
python -m src.main run "Build a blog with Next.js and FastAPI, include auth and database"
```

### With Custom Workspace
```bash
python -m src.main run "Create a REST API" --workspace ./my-project
```

### Use Specific LLM
```bash
python -m src.main run "Create a game" --provider anthropic --model claude-3-5-sonnet-20241022
```

## Architecture

```
src/
├── core/           # Main orchestration
│   ├── orchestrator.py  # Agent brain
│   ├── llm.py           # LLM integration
│   └── config.py        # Configuration
├── tools/          # Agent actions
│   ├── file_ops.py      # File operations
│   └── terminal.py      # Command execution
├── search/         # Smart code navigation (Phase 2)
├── healing/        # Self-healing engine (Phase 4)
└── templates/      # Code generation templates (Phase 3)
```

## Current Status: Phase 1 ✓

✅ LLM integration (OpenAI + Anthropic)  
✅ Tool system with file operations  
✅ Terminal command execution  
✅ Basic orchestrator  
✅ CLI interface  

Coming Next (Phase 2):
- Smart search engine
- AST parsing
- Semantic code search

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Check Configuration
```bash
python -m src.main config
```

### Version
```bash
python -m src.main version
```

## Requirements

- Python 3.11+
- OpenAI API key OR Anthropic API key
- Git (optional)

## License

MIT License

## Contributing

See [ARCHITECTURE_AND_PLAN.md](ARCHITECTURE_AND_PLAN.md) for the complete implementation roadmap.
