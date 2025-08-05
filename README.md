# 🎬 Video Downloader MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**Give your agents the ability to download videos from 1000+ sites with built-in security.** This MCP server provides 7 discrete tools that agents can use to check, analyze, and download videos from nearly any web page. Built on yt-dlp with security validation and fallback analysis.

## 🌟 Features

- **🛠️ 7 MCP Tools** - Discrete capabilities for checking, analyzing, and downloading videos
- **🔒 Built-in Security** - Path validation, location restrictions, and input sanitization
- **🌐 1000+ Sites Supported** - YouTube, Facebook, TikTok, and hundreds more via yt-dlp
- **🔄 Fallback Analysis** - Pattern matching when yt-dlp doesn't support a site
- **📁 Organized Downloads** - Configurable secure locations with filename templates
- **⚙️ Agent-Friendly** - Clean JSON responses and structured error handling

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install mcp yt-dlp requests aiohttp

# For Python < 3.11, also install:
pip install tomli

# Clone the repository
git clone https://github.com/chazmaniandinkle/video-downloader-mcp.git
cd video-downloader-mcp
```

### Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "video-downloader": {
      "command": "python",
      "args": ["/path/to/video-downloader-mcp/server.py"]
    }
  }
}
```

### First Download

Your agent can now download videos with simple tool calls:

```python
# Agent workflow example
1. check_ytdlp_support("https://youtube.com/watch?v=example")  # → supported: true
2. get_video_formats(url)  # → analyze available qualities
3. download_video(url, location_id="default", format_id="best")  # → download to ~/video-downloader/
```

## 🛠️ Available Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `check_ytdlp_support` | Quick URL validation | "Is this video URL supported?" |
| `get_video_info` | Extract metadata | "What's the video duration and quality?" |
| `get_video_formats` | List quality options | "What download formats are available?" |
| `download_video` | Secure download | "Download this video in 1080p" |
| `get_download_locations` | Show safe locations | "Where can I save downloaded files?" |
| `analyze_webpage` | Fallback analysis | "yt-dlp failed, analyze the page" |
| `extract_media_patterns` | Pattern matching | "Find video URLs in this HTML" |

## 🔒 Security Features

### Built-in Protection
- **Path Traversal Prevention** - Blocks `../` directory escape attempts
- **Location Restrictions** - Downloads only to configured safe directories  
- **Extension Validation** - Allows only safe file types (video/audio/subtitles)
- **Template Sanitization** - Removes dangerous shell characters
- **TOML Configuration** - No deserialization vulnerabilities

### Secure Download Example
```json
{
  "url": "https://example.com/video",
  "location_id": "default",          // Uses configured secure location
  "relative_path": "movies/action",  // Validated relative path  
  "filename_template": "%(title)s.%(ext)s"  // Sanitized template
}
```

### Default Security Configuration
```toml
[security]
enforce_location_restrictions = true
max_filename_length = 255
allowed_extensions = ["mp4", "webm", "mkv", "avi", "mov", "m4a", "mp3", "aac", "ogg", "wav", "vtt", "srt"]
block_path_traversal = true

[download_locations]
default = "~/video-downloader"
```

## 🎯 Agent Integration Examples

### Simple Video Download
```bash
User: "Download this YouTube video in good quality"
Agent: 
→ check_ytdlp_support("https://youtube.com/watch?v=dQw4w9WgXcQ")  # ✓ supported
→ get_video_formats(url)  # finds 720p format
→ download_video(url, format_id="22", location_id="default")  # downloads to ~/video-downloader/
```

### Quality-Aware Selection  
```bash
User: "Get the best quality under 100MB"
Agent: 
→ get_video_formats(url)  # lists all formats with sizes
→ [agent analyzes: 480p=45MB, 720p=95MB, 1080p=180MB]
→ download_video(url, format_id="720p")  # selects 95MB option
```

### Chained with Web Search
```bash
User: "Find and download the latest Corridor Crew video"
Agent:
→ web_search("Corridor Crew latest video YouTube")  # finds URL
→ check_ytdlp_support(found_url)  # ✓ supported  
→ download_video(found_url, location_id="default")
```

### Unsupported Site Analysis
```bash
User: "This custom streaming site has a video I need"
Agent:
→ check_ytdlp_support(url)  # ✗ not supported
→ analyze_webpage(url)  # finds video player type  
→ extract_media_patterns(url)  # extracts manifest URLs
→ [returns streaming URLs for manual processing]
```

## ⚙️ Configuration

The server creates `~/.config/video-downloader-mcp/config.toml` automatically. Customize as needed:

```toml
[download_locations]
default = "~/video-downloader"
movies = "~/Movies/Downloads"  
music = "~/Music/Downloads"
temp = "/tmp/video-downloads"

[security]
enforce_location_restrictions = true
max_filename_length = 255
allowed_extensions = [
    "mp4", "webm", "mkv", "avi", "mov",    # Video
    "m4a", "mp3", "aac", "ogg", "wav",     # Audio
    "vtt", "srt", "ass", "ssa"             # Subtitles
]

[ytdlp]  
default_format = "best[height<=1080]"
default_filename_template = "%(title)s.%(ext)s"

[logging]
log_security_events = true
log_downloads = true
```

## 🧠 LLM Integration Examples

### With Claude Code
```
You: Download this Corridor Crew video in the highest quality available

Claude: I'll help you download that video. Let me check what formats are available and download the best quality.

[Uses check_ytdlp_support → get_video_formats → download_video]

✅ Downloaded: "VFX Artists React to MEGALOPOLIS" (1080p, 250MB)
📁 Location: ~/video-downloader/VFX Artists React to MEGALOPOLIS.mp4
```

### With ChatGPT + MCP
```
User: Get video information for this educational YouTube video and download the audio-only version

ChatGPT: I'll extract the video information and download just the audio for you.

[Uses get_video_info → analyzes metadata → download_video with audio format]

📊 Video Info: "Introduction to Machine Learning" (45:32 duration)
🎵 Downloaded: Audio-only version (m4a, 42MB)
```

## 🏗️ MCP Architecture Patterns

This server demonstrates several reusable patterns for building secure, agent-friendly MCP servers:

### Tool Declaration Pattern
```python
# Reusable pattern for tool definitions
types.Tool(
    name="check_ytdlp_support",
    description="Check if a URL is supported by yt-dlp and get basic info",
    inputSchema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Video URL to check"}
        },
        "required": ["url"]
    }
)
```

### Security Validation Pattern
```python
# Multi-layer security validation
def validate_and_construct_path(self, location_id: str, relative_path: str):
    # 1. Validate location exists in config
    # 2. Check path traversal attempts  
    # 3. Canonicalize and verify boundaries
    # 4. Sanitize filename templates
    return validated_path
```

### Structured Response Pattern
```python
# Consistent success/error responses
try:
    result = perform_operation()
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

### Configuration Management Pattern
```python
# TOML-based secure configuration
class SecureConfigManager:
    def __init__(self):
        self.config_path = Path.home() / ".config" / "app-name" / "config.toml"
        self.load_or_create_default()
    
    def get(self, key_path: str, default=None):
        # Safe nested key access with defaults
```

### Testing

```bash
# Run security tests
python test_security.py

# Test MCP tool functionality  
python test_mcp_security.py

# Run comprehensive workflow tests
python test_final_comprehensive.py
```

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/your-username/video-downloader-mcp.git
cd video-downloader-mcp

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black .
isort .
```

## 📋 Requirements

- **Python 3.8+**
- **yt-dlp** (latest version recommended)  
- **MCP library** (`pip install mcp`)
- **Additional dependencies**: `requests`, `aiohttp`, `tomli` (Python < 3.11)

## 🔍 Troubleshooting

### Common Issues

**MCP server not loading:**
```bash
# Check MCP configuration
# Ensure full absolute path to server.py
# Verify Python environment has required packages
```

**Downloads failing:**
```bash
# Check yt-dlp installation
yt-dlp --version

# Verify download directory permissions  
ls -la ~/video-downloader

# Check configuration
cat ~/.config/video-downloader-mcp/config.toml
```

**Security validation errors:**
```bash
# Check that paths don't contain ../
# Verify location_id exists in configuration
# Ensure file extensions are in allowed list
```

### Debug Mode

```bash
# Enable verbose logging
export MCP_DEBUG=1
export YTDLP_DEBUG=1
python server.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - The powerful video extraction engine that makes this possible
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Enabling seamless LLM-tool integration
- **[Anthropic](https://anthropic.com/)** - For Claude and the MCP specification

## 🚀 Related Projects

- [MCP Specification](https://spec.modelcontextprotocol.io/) - Official MCP documentation
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - Claude's code editing environment
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The underlying video extraction library

---

**Give your agents video downloading capabilities across 1000+ platforms.** 🎬