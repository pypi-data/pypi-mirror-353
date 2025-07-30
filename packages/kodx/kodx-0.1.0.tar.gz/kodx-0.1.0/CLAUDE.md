# CLAUDE.md - Kodx Project Context

## Project Overview

Kodx is a minimal Docker-based code execution environment designed for LLM integration. It provides exactly 2 tools for LLMs to interact with containerized development environments through natural shell commands.

**Core Principle**: Follow llmproc CLI patterns exactly while adding container isolation and local directory support.

## Current Architecture (Post-Refactoring)

### CLI Interface
Kodx now follows llmproc's single-command pattern:
```bash
kodx [PROGRAM_PATH] [options]
```

**Key Changes from v1:**
- **Optional program files** - Uses built-in assistant if not specified
- **Smart --repo-dir** - Defaults to current directory if not specified
- **Single command** - removed run/ask subcommands
- **JSON output** - compatible with automation and CI/CD (--json or --json-output-file)
- **Export functionality** - --export-dir for GitHub automation workflows
- **Cost control** - --cost-limit to manage API spending

### Project Structure
```
kodx/
├── src/kodx/
│   ├── cli.py              # Refactored CLI following llmproc pattern
│   ├── tools.py            # DockerCodexTools with 2 @register_tool methods
│   ├── codex_shell.py      # CodexShell for PTY server communication
│   ├── defaults.py         # Built-in default assistant program
│   └── __init__.py         # Package exports
├── .github/config/         # Production LLM programs
│   ├── kodx-ask-program.yaml   # Code analysis expert (GitHub workflows)
│   └── kodx-code-program.yaml  # Code implementation expert (GitHub workflows)
├── docs/                   # Technical documentation
└── README.md              # User-facing documentation
```

## Tool Interface (LLM Perspective)

Kodx exposes exactly **2 tools** to LLMs:

### `feed_chars(chars: str) -> str`
Primary interface for all shell interaction:
- Execute commands: `feed_chars("ls -la")`
- Create files: `feed_chars("cat > file.py\nprint('hello')\n")`
- Send Ctrl+C: `feed_chars("\x03")`
- Run interactive programs: `feed_chars("python")`

### `create_new_shell() -> str`
Reset environment when needed:
- Fresh shell session
- Clean environment state
- Return to /workspace directory

## Key Design Decisions

1. **Follow llmproc exactly** - Program files are required, CLI patterns match
2. **Explicit behavior** - No magic defaults, all actions explicit via flags
3. **Local directory focus** - Simple file copying, no git clone complexity
4. **Container isolation** - Each session gets clean Docker environment
5. **JSON automation** - Structured output for CI/CD integration

## Development Workflow

### Session Setup
- Review tool interface in `tools.py` (only 2 methods with `@register_tool`)
- Check production programs in `.github/config/` directory
- Read technical docs in `docs/` directory

### Testing Current Interface
```bash
# Install in development mode with all extras
uv sync --all-extras --group dev

# Test with default assistant
kodx --prompt "Create a hello world script"  # Uses current directory
kodx --repo-dir "" --prompt "Create hello world"  # Clean container

# Test with production programs
kodx .github/config/kodx-code-program.yaml --repo-dir "" --prompt "Create hello world"
kodx .github/config/kodx-ask-program.yaml --repo-dir . --prompt "Analyze this project"

# Test JSON output (to stdout or file)
kodx --prompt "Quick scan" --json
kodx --prompt "Quick scan" --json-output-file results.json
```

### Implementation Notes

#### Docker Container Flow
1. Create container with `sleep infinity`
2. Install dependencies (curl, fastapi, uvicorn)
3. Deploy embedded PTY server code to `/root/pty_server.py`
4. Start PTY server on localhost:1384
5. Create bash session via HTTP POST to `/open`
6. Setup `/workspace` directory
7. Ready for `feed_chars` commands

#### PTY Server Communication
- All shell interaction goes through HTTP endpoints
- PTY provides full terminal capabilities (colors, signals, interactive programs)
- Commands sent via `/write/{pid}`, output read via `/read/{pid}`
- Session cleanup via `/kill/{pid}`

#### Tool Registration
Uses llmproc's enhanced `@register_tool` decorator that supports class methods:
```python
@register_tool(description="Send characters/commands to the shell")
async def feed_chars(self, chars: str) -> str:
    # Implementation uses CodexShell.run()
```

## Integration with llmproc

Kodx is built on [llmproc](https://github.com/cccntu/llmproc-private):
- Uses standard llmproc configuration (primarily YAML, also supports TOML)
- Leverages llmproc's tool registration system
- Follows llmproc CLI patterns and options
- Integrates with llmproc's provider system (Anthropic, OpenAI, etc.)

### Docker Configuration in Program Files

Program YAML files can include Docker configuration:
```yaml
model:
  name: "claude-3-5-sonnet-20241022"
  provider: "anthropic"

docker:
  image: "python:3.11"  # Optional, defaults to python:3.11
  disable_network_after_setup: true  # Optional, enhances security isolation
  setup_script: |
    pip install flask pytest
    apt-get update && apt-get install -y git
```

## Common Usage Patterns

### Default Assistant (Most Common)
```bash
# Analyze current directory (default behavior)
kodx --prompt "What is the architecture of this project?"

# Work in clean container
kodx --repo-dir "" --prompt "Create a Python web app with Flask"

# Work with specific directory
kodx --repo-dir ./my-project --prompt "Run the tests"
```

### Repository Analysis
```bash
# Using default assistant
kodx --prompt "Review the code quality"

# Using specialized code analysis expert
kodx .github/config/kodx-ask-program.yaml --repo-dir . --prompt "What is the architecture?"

# With cost control
kodx --prompt "Review code" --cost-limit 0.50
```

### Setup Scripts
```bash
# Execute setup script before task (via CLI)
kodx .github/config/kodx-code-program.yaml --repo-dir . --setup-script setup.sh --prompt "Run tests"

# Execute setup script with network isolation for security
kodx .github/config/kodx-code-program.yaml --repo-dir . --setup-script setup.sh --disable-network-after-setup --prompt "Secure analysis"

# Or define in program YAML file:
# docker:
#   setup_script: "pip install -r requirements.txt"
#   disable_network_after_setup: true  # For security isolation
```

### Development Tasks
```bash
# Create new application
kodx .github/config/kodx-code-program.yaml --repo-dir "" --prompt "Create FastAPI server" --export-dir ./new-app

# Debug existing code with export
kodx .github/config/kodx-code-program.yaml --repo-dir . --prompt "Fix error in cli.py" --export-dir ./bugfixes
```

### GitHub Automation
```bash
# CI/CD integration with export
kodx .github/config/kodx-ask-program.yaml --repo-dir . --prompt "Generate report and fixes" --export-dir ./changes --json-output-file results.json

# GitHub Actions workflow
- run: |
    kodx .github/config/kodx-ask-program.yaml --repo-dir . --prompt "Generate report" --export-dir ./changes --json-output-file results.json
    cp -r changes/* .
    git add . && git commit -m "Apply automated code review"
```

### LLM Tool Usage (within programs)
```python
# File operations
feed_chars("cat > script.py << EOF\nimport sys\nprint(sys.version)\nEOF")

# Package management
feed_chars("pip install requests flask")

# Process control
feed_chars("python -c 'print(\"hello\")'")
feed_chars("\x03")  # Ctrl+C
create_new_shell()  # Reset if needed
```

## Error Handling Strategy

- **Container failures**: Clear error messages, graceful fallback
- **PTY server issues**: Health checks, automatic retries
- **Shell problems**: `create_new_shell()` for recovery
- **Command hangs**: `feed_chars("\x03")` for interruption

## Security Model

- Each session gets isolated Docker container
- Containers auto-removed on exit
- No persistent storage by default
- PTY server only accessible from within container
- No direct host system access
- Optional network isolation after setup with `--disable-network-after-setup` for enhanced security

## Extension Guidelines

When extending Kodx:

1. **Prefer shell commands** over new tools
2. **Keep interface minimal** - can the task be done with existing tools?
3. **Follow container isolation** - don't break the security model
4. **Document in [docs/index.md](docs/index.md)** - maintain architectural documentation
5. **Test with multiple images** - ensure compatibility

## Related Files

- **[docs/index.md](docs/index.md)** - Complete technical architecture documentation
- **[README.md](README.md)** - User-facing documentation and quick start
- **[.github/config/](.github/config/)** - Production LLM program files (YAML format)
- **[src/kodx/tools.py](src/kodx/tools.py)** - Core tool implementation
- **[tests/](tests/)** - Comprehensive test suite (unit, integration, system, performance)

This project maintains a Unix philosophy: do one thing well, with a minimal and composable interface.
