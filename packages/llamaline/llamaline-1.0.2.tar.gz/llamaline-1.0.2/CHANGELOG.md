# Changelog

## [1.0.2] - 2024-12-19 - CI/CD Fixes and PyPI Release 🚀

### 🛠 CI/CD Fixes
- **GitHub Actions**: Fixed workflow branch triggers to support master branch
- **Test Workflows**: Updated test matrix to run on correct branches
- **Release Automation**: Streamlined release process for PyPI publishing
- **Version Synchronization**: Updated all version references to 1.0.2

### 🚀 PyPI Deployment
- **Automated Publishing**: GitHub Actions workflow configured for PyPI
- **Package Validation**: Enhanced testing pipeline before release
- **Distribution**: Ready for automated PyPI publishing via OIDC

---

## [1.0.1] - 2024-12-19 - Bug Fixes and CI/CD Improvements 🔧

### 🛠 Bug Fixes
- **Conda Recipe**: Removed LICENSE file references that were causing build failures
- **Permission Issues**: Fixed git permission conflicts between root and regular user
- **Version Synchronization**: Updated all version references to 1.0.1
- **Build System**: Removed setup.py conflicts with pyproject.toml

### 🚀 Improvements
- **Test Validation**: Added comprehensive `scripts/test_package.sh` script
- **CI/CD Workflows**: Enhanced GitHub Actions with better error handling
- **Package Building**: Streamlined build process with proper validation
- **Documentation**: Added workflow summary and troubleshooting guides

### ✅ Validation
- Package builds successfully with `python -m build`
- Passes `twine check` validation
- CLI functionality confirmed working
- Import and basic functionality tested

---

## [1.0.0] - 2024-12-19 - First Stable Release 🎉

### 🚀 New Features
- **Natural Language Processing**: Convert English prompts to executable bash/Python code using local Ollama models
- **Interactive CLI**: Rich-styled command-line interface with colorized output and confirmation prompts
- **Cheat Sheet Library**: Predefined shortcuts for common tasks (disk usage, file listing, process monitoring, etc.)
- **Safety Features**: Command confirmation, unsafe operation blocking, and dry-run previews
- **Flexible Configuration**: Environment variable and CLI flag overrides for Ollama endpoint and model selection
- **Single-Shot Execution**: Run commands directly from CLI arguments (`llamaline "show disk usage"`)
- **Model Switching**: Change Ollama models on-the-fly during interactive sessions

### 🛠 Core Capabilities
- **Python Execution**: Execute Python snippets in temporary files with pretty-printed JSON output
- **Bash Execution**: Run shell commands with safety checks to prevent destructive operations
- **Rich Output**: Formatted console output with syntax highlighting and panels
- **Error Handling**: Comprehensive error reporting and graceful failure handling

### 🎯 Accessibility Features
- Keyboard-only navigation (no mouse required)
- Colorized output with plain text fallbacks
- Clear command structure and help system
- Screen reader compatible interface

### 📦 Technical Implementation
- Built on Python 3.7+ with asyncio for command execution
- Integration with local Ollama models (default: gemma3:4b)
- Dependencies: colorama, rich, requests
- MIT License with comprehensive documentation

### 🔧 Development & Distribution
- Installable via pip (`pip install .` or `pip install -e .` for development)
- Entry point: `llamaline` command available system-wide
- Package structure following Python best practices

---

## [0.1.0] - Initial package
- Project structure reorganized as a package named `llamaline`
- Added setup.py and pyproject.toml
- Added CLI entry point `llamaline`
- Added README and accessibility notes 