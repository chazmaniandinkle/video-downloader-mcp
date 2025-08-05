# 🎬 Video Downloader MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A powerful **Model Context Protocol (MCP) server** that transforms video downloading into a tool-based system for LLM orchestration. Built on yt-dlp with comprehensive security features and intelligent fallback mechanisms.

## 🌟 Features

- **🛠️ 7 MCP Tools** for intelligent video processing workflows
- **🔒 Enterprise Security** with path validation and sandboxed downloads
- **🌐 1000+ Platforms** supported via yt-dlp integration
- **🧠 LLM-Orchestrated** workflows with granular tool control
- **🔄 Fallback Analysis** for unsupported sites
- **📁 Organized Downloads** with configurable secure locations
- **⚡ High Performance** with efficient format selection

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install mcp yt-dlp requests aiohttp

# For Python < 3.11, also install:
pip install tomli

# Clone the repository
git clone https://github.com/your-username/video-downloader-mcp.git
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

```python
# Example: LLM workflow for downloading a video
1. check_ytdlp_support("https://youtube.com/watch?v=example")
2. get_video_formats(url) → analyze quality options  
3. download_video(url, location_id="default", format_id="best")
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

## 🎯 Usage Examples

### Basic Video Download
```bash
# LLM: "Download this YouTube video in good quality"
→ check_ytdlp_support("https://youtube.com/watch?v=dQw4w9WgXcQ")
→ get_video_formats(url) 
→ download_video(url, format_id="720p", location_id="default")
```

### Quality Selection Workflow  
```bash
# LLM: "Show me all available qualities and download the best one under 100MB"
→ get_video_formats(url)
→ [LLM analyzes format sizes]
→ download_video(url, format_id="selected_format")
```

### Fallback Analysis
```bash
# LLM: "This site isn't supported by yt-dlp, can you analyze it?"
→ check_ytdlp_support(url) → fails
→ analyze_webpage(url) 
→ extract_media_patterns(url)
→ [Returns manifest URLs and video files found]
```

### Organized Downloads
```bash
# LLM: "Download this to my Movies folder in the 'documentaries' subfolder"
→ get_download_locations()
→ download_video(url, location_id="movies", relative_path="documentaries")
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

## 🔧 Development

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Client    │───▶│   MCP Server    │───▶│   yt-dlp Core   │
│  (Claude, etc.) │    │  (This Project) │    │  (Video Engine) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────▶│ Fallback Tools  │◀─────────────┘
                        │  (Web Analysis) │
                        └─────────────────┘
```

### Key Components

- **YtDlpExtractor**: Wraps yt-dlp with structured interfaces
- **WebpageAnalyzer**: Fallback analysis for unsupported sites  
- **SecureConfigManager**: TOML-based configuration with security defaults
- **PathValidator**: Multi-layer path security validation
- **LocationManager**: Manages configured download locations

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

**Transform your video downloading workflow with intelligent LLM orchestration!** 🎬✨