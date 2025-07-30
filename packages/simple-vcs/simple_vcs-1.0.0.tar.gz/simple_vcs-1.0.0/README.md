# README.md
# SimpleVCS

A simple version control system written in Python that provides basic VCS functionality similar to Git.

## Features

- Initialize repositories
- Add files to staging area
- Commit changes with messages or timestamps
- View commit history with detailed information
- Show differences between commits
- Repository status tracking
- Cross-platform compatibility
- Both CLI and Python API support

## Installation

### From PyPI (when published)
```bash
pip install simple-vcs
```

### From Source
```bash
# Clone the repository
git clone https://github.com/muhammadsufiyanbaig/simple_vcs.git
cd simple-vcs

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

## Quick Start

```bash
# Initialize a new repository
svcs init

# Create a sample file
echo "Hello World" > hello.txt

# Add file to staging area
svcs add hello.txt

# Commit the changes
svcs commit -m "Add hello.txt"

# View commit history
svcs log
```

## Usage

### Command Line Interface

#### Repository Management
```bash
# Initialize a new repository in current directory
svcs init

# Initialize in specific directory
svcs init --path /path/to/project
```

#### File Operations
```bash
# Add single file
svcs add filename.txt

# Add multiple files
svcs add file1.txt file2.py file3.md

# Check repository status
svcs status
```

#### Commit Operations
```bash
# Commit with message
svcs commit -m "Your commit message"

# Commit with auto-generated timestamp
svcs commit

# View commit history
svcs log

# View limited commit history
svcs log --limit 5
```

#### Viewing Differences
```bash
# Show diff between last two commits
svcs diff

# Show diff between specific commits
svcs diff --c1 1 --c2 3

# Show diff between commit 2 and latest
svcs diff --c1 2
```

### Python API

```python
from simple_vcs import SimpleVCS

# Create VCS instance
vcs = SimpleVCS("./my_project")

# Initialize repository
vcs.init_repo()

# Add files
vcs.add_file("example.txt")
vcs.add_file("script.py")

# Commit changes
vcs.commit("Initial commit with example files")

# Show commit history
vcs.show_log()

# Show differences between commits
vcs.show_diff(1, 2)

# Check repository status
vcs.status()
```

## Advanced Usage

### Working with Multiple Files
```python
from simple_vcs import SimpleVCS
from simple_vcs.utils import get_all_files

vcs = SimpleVCS()
vcs.init_repo()

# Add all Python files in current directory
python_files = [f for f in get_all_files(".") if f.endswith('.py')]
for file in python_files:
    vcs.add_file(file)

vcs.commit("Add all Python files")
```

### Repository Structure
When initialized, SimpleVCS creates a `.svcs` directory containing:
```
.svcs/
├── objects/          # File content storage (hashed)
├── commits.json      # Commit history and metadata
├── staging.json      # Currently staged files
└── HEAD             # Current commit reference
```

## Requirements

- Python 3.7 or higher
- click>=7.0 (for CLI functionality)

## Development

### Setting up Development Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/simple-vcs.git
cd simple-vcs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=simple_vcs

# Run specific test file
pytest tests/test_core.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Publishing to PyPI

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (requires PyPI account)
twine upload dist/*
```

## Limitations

This is a simple implementation for educational purposes. It lacks advanced features like:
- Branching and merging
- Remote repositories
- File conflict resolution
- Large file handling
- Advanced diff algorithms

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Your Name - your.email@example.com

## Changelog

### Version 1.0.0
- Initial release
- Basic VCS functionality (init, add, commit, log, diff, status)
- CLI and Python API support
- Cross-platform compatibility