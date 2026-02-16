# Contributing to Castle Wyvern

Thank you for your interest in contributing to Castle Wyvern! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/castle-wyvern.git
   cd castle-wyvern
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install with dev dependencies
   ```

4. Run tests to ensure everything works:
   ```bash
   pytest tests/ -v
   ```

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)
- Any relevant error messages or logs

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Why it would be useful
- Any implementation ideas you have

### Pull Requests

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Add or update tests as needed
4. Ensure all tests pass:
   ```bash
   pytest tests/ -v
   ```

5. Commit your changes with a clear message:
   ```bash
   git commit -m "Add feature: description of what you did"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Open a Pull Request on GitHub

## Code Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use Black for code formatting:
  ```bash
  black .
  ```

### Testing

- All new features should include tests
- All bug fixes should include a test that reproduces the bug
- Aim for high test coverage
- Run tests before submitting PR:
  ```bash
  pytest tests/ -v
  ```

### Documentation

- Update README.md if you change functionality
- Add docstrings to new functions and classes
- Keep comments clear and concise

## Project Structure

```
castle-wyvern/
├── eyrie/              # Core modules
├── grimoorum/          # Additional utilities
├── bmad/               # CLI commands
├── clan_members/       # Agent definitions
├── spells/             # Workflow spells
├── tests/              # Test suite
├── docs/               # Documentation
└── castle_wyvern_cli.py  # Main CLI entry point
```

## Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs where appropriate

Examples:
```
Add support for custom clan member backstories

Fix memory leak in knowledge graph operations

Update README with installation instructions

Closes #123
```

## Code Review Process

1. Maintainers will review your PR as soon as possible
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR

## Areas for Contribution

We're particularly interested in contributions to:

- **Testing**: Expanding test coverage
- **Documentation**: Improving docs, tutorials, examples
- **Integrations**: Adding support for new LLM providers or tools
- **Performance**: Optimizing existing code
- **Bug fixes**: Fixing reported issues
- **New features**: Check the issues for requested features

## Questions?

If you have questions about contributing:
- Check existing issues and PRs
- Open a new issue with the "question" label
- Join discussions in existing issues

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what's best for the project
- Accept constructive criticism gracefully

Thank you for contributing to Castle Wyvern! 🏰
