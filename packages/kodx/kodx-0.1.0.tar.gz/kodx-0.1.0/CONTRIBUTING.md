# Contributing to Kodx

Thank you for your interest in contributing to Kodx! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.9+
- Docker (for testing containerized functionality)
- Git

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/kodx/kodx
cd kodx
```

2. **Create virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install in development mode**:
```bash
pip install -e ".[dev]"
```

4. **Install pre-commit hooks** (optional but recommended):
```bash
pre-commit install
```

## Development Workflow

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_cli.py

# Run with coverage
pytest --cov=kodx

# Run only fast tests (no Docker)
pytest -m "not integration"
```

### Code Style
We use `ruff` for code formatting and linting:

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Testing the CLI
```bash
# Test basic functionality
python -m kodx.cli run --help

# Test ask feature (requires API key)
export ANTHROPIC_API_KEY="your-key-here"
python -m kodx.cli ask --repo-url https://github.com/owner/repo --query "test query"
```

## Contributing Guidelines

### Pull Request Process

1. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**:
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
```bash
pytest
ruff check .
```

4. **Commit your changes**:
```bash
git add .
git commit -m "feat: describe your changes"
```

5. **Submit a pull request**:
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all checks pass

### Commit Message Convention

We follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes  
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### Code Standards

1. **Type Hints**: Use type hints for all function parameters and return values
2. **Docstrings**: Provide clear docstrings for all public functions and classes
3. **Error Handling**: Include appropriate error handling and logging
4. **Testing**: Write tests for all new functionality

### Architecture Principles

Kodx follows these design principles:

1. **Minimal Interface**: Keep the tool interface simple (2 tools only)
2. **Security First**: Never expose credentials in containers
3. **Container Isolation**: Each execution runs in a clean environment
4. **Unix Philosophy**: Use standard shell commands over custom wrappers

## Project Structure

```
kodx/
├── src/kodx/          # Main package
│   ├── cli.py             # CLI commands
│   ├── tools.py           # Docker tools implementation
│   ├── codex_shell.py     # Shell interaction
│   └── __init__.py        # Package exports
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── system/            # System tests
│   └── performance/       # Performance tests
├── docs/                  # Documentation
├── examples/              # Example configurations
└── .github/               # GitHub workflows
```

## Areas for Contribution

### High Priority
- [ ] Additional Docker image support
- [ ] Performance optimizations
- [ ] Enhanced error messages
- [ ] Documentation improvements

### Medium Priority
- [ ] Additional CLI features
- [ ] Integration with other LLM providers
- [ ] Monitoring and metrics
- [ ] Configuration validation

### Low Priority
- [ ] GUI interface
- [ ] Plugin system
- [ ] Advanced container management

## Getting Help

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the `docs/` directory for detailed information

## Security

When contributing, please:
- Never commit API keys or secrets
- Follow secure coding practices
- Report security issues privately via email

## License

By contributing to Kodx, you agree that your contributions will be licensed under the Apache License 2.0.
