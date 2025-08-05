# Contributing to Video Downloader MCP Server

Thank you for your interest in contributing! This project welcomes contributions from the community.

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- yt-dlp (latest version)

### Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/chazmaniandinkle/video-downloader-mcp.git
   cd video-downloader-mcp
   ```

2. **Set up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install mcp yt-dlp requests aiohttp
   pip install tomli  # For Python < 3.11
   
   # Install development dependencies
   pip install black isort mypy pytest
   ```

3. **Run Tests**
   ```bash
   # Test security framework
   python test_security.py
   
   # Test MCP tools
   python test_mcp_security.py
   
   # Comprehensive tests
   python test_final_comprehensive.py
   ```

## 🎯 How to Contribute

### Reporting Issues
- Use GitHub Issues for bug reports and feature requests
- Include clear reproduction steps for bugs
- Provide environment details (Python version, OS, etc.)

### Contributing Code

1. **Choose an Issue**
   - Look for issues labeled `good first issue` or `help wanted`
   - Comment on the issue to let others know you're working on it

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow the existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run all tests
   python test_security.py
   python test_mcp_security.py
   python test_final_comprehensive.py
   
   # Format code
   black .
   isort .
   
   # Type checking
   mypy server.py
   ```

5. **Submit a Pull Request**
   - Write a clear description of your changes
   - Reference any related issues
   - Include test results

## 🏗️ Project Structure

```
video-downloader-mcp/
├── server.py              # Main MCP server implementation
├── config.toml            # Default configuration
├── pyproject.toml         # Python package configuration
├── README.md              # Project documentation
├── SECURITY.md            # Security documentation
├── CLAUDE.md              # Development context for Claude
├── test_*.py              # Test files
└── LICENSE                # MIT License
```

## 🔧 Development Guidelines

### Code Style
- Use **Black** for code formatting
- Use **isort** for import sorting
- Follow **PEP 8** naming conventions
- Add type hints where appropriate

### Security Considerations
- All path operations must use `PathValidator`
- Never bypass security validation
- Sanitize user input thoroughly
- Document security implications of changes

### Testing Requirements
- Add tests for new features
- Ensure security tests pass
- Test with real video URLs when safe
- Mock external dependencies where appropriate

### Documentation
- Update README.md for user-facing changes
- Update SECURITY.md for security-related changes
- Add docstrings for new functions/classes
- Include examples for new MCP tools

## 🎨 Adding New MCP Tools

To add a new MCP tool:

1. **Define the tool** in `handle_list_tools()`:
   ```python
   types.Tool(
       name="your_tool_name",
       description="Clear description of what the tool does",
       inputSchema={
           "type": "object",
           "properties": {
               "url": {"type": "string", "description": "Video URL"}
           },
           "required": ["url"]
       }
   )
   ```

2. **Implement the handler** in `handle_call_tool()`:
   ```python
   elif name == "your_tool_name":
       url = arguments["url"]
       try:
           result = your_implementation(url)
           return [types.TextContent(
               type="text",
               text=json.dumps({"success": True, "data": result})
           )]
       except Exception as e:
           return [types.TextContent(
               type="text",
               text=json.dumps({"success": False, "error": str(e)})
           )]
   ```

3. **Add tests** for the new tool
4. **Update documentation** with usage examples

## 🔒 Security Guidelines

### Input Validation
- Validate all URLs and paths
- Use `PathValidator` for any file operations
- Never execute user-provided code directly
- Sanitize filename templates

### Path Security
- All downloads must use configured locations
- Block path traversal attempts (`../`, etc.)
- Validate file extensions against allowlist
- Use `LocationManager` for path construction

### Error Handling
- Don't expose sensitive information in error messages
- Log security events appropriately
- Return structured error responses

## 🏷️ Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes to MCP tool interfaces
- **MINOR**: New features, new MCP tools
- **PATCH**: Bug fixes, security updates

## 📝 Commit Message Format

Use clear, descriptive commit messages:

```
type(scope): brief description

Longer description if needed

- Detail 1
- Detail 2

Fixes #123
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting
- `refactor`: Code refactoring
- `test`: Test changes
- `security`: Security improvements

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a welcoming environment

## ❓ Questions?

- Open a GitHub Discussion for general questions
- Join our community discussions
- Check existing issues and documentation first

## 🙏 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- GitHub contributor stats
- Release notes for significant contributions

Thank you for helping improve agent video downloading capabilities! 🎬