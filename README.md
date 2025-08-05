# Video Downloader MCP Server

An MCP (Model Context Protocol) server that exposes video downloading and analysis capabilities as tools for LLM clients. This allows LLMs to intelligently orchestrate video extraction workflows using yt-dlp and fallback analysis methods.

## 🎯 Architecture Philosophy

This project reimagines the original monolithic video downloader as a **tool-based system** where:

- **LLMs make intelligent decisions** about which tools to use and when
- **yt-dlp handles the heavy lifting** for supported sites (1000+ platforms)
- **Fallback analysis tools** provide options when yt-dlp fails
- **Granular control** allows LLMs to orchestrate complex workflows

## 🛠️ Available Tools

### Core Video Tools

#### `check_ytdlp_support`
Quick check if a URL is supported by yt-dlp with basic metadata.

**Input**: `{"url": "https://example.com/video"}`
**Output**: Supported status, title, duration, uploader info

#### `get_video_info` 
Comprehensive video information extraction.

**Input**: `{"url": "https://example.com/video"}`
**Output**: Full metadata, format count, subtitle languages

#### `get_video_formats`
List all available video/audio formats and quality options.

**Input**: `{"url": "https://example.com/video"}`
**Output**: Detailed format list with codecs, resolutions, file sizes

#### `download_video`
Securely download video with format and location options.

**Input (Secure)**: 
```json
{
  "url": "https://example.com/video",
  "location_id": "default",           // configured download location
  "relative_path": "movies",          // optional subdirectory
  "filename_template": "%(title)s.%(ext)s",  // optional template
  "format_id": "137"                  // optional format
}
```

**Input (Legacy - Deprecated)**: 
```json
{
  "url": "https://example.com/video",
  "output_path": "%(title)s.%(ext)s"  // bypasses security validation
}
```
**Output**: Download status, secure path, and logs

#### `get_download_locations`
List configured secure download locations.

**Input**: `{}` (no parameters)
**Output**: Available locations with write permissions and descriptions

### Fallback Analysis Tools

#### `analyze_webpage`
Analyze webpage structure when yt-dlp fails.

**Input**: `{"url": "https://custom-site.com/video"}`
**Output**: Metadata, content analysis, video tag detection

#### `extract_media_patterns`
Extract video/audio URLs using pattern matching.

**Input**: `{"url": "https://custom-site.com/video"}`
**Output**: Manifest URLs, video files, audio files, subtitles

## 🚀 Example LLM Workflows

### Simple Download
```
1. LLM calls check_ytdlp_support(url)
2. If supported → calls download_video(url)
3. If not supported → calls analyze_webpage(url) → extract_media_patterns(url)
```

### Quality Selection
```
1. LLM calls get_video_formats(url)
2. LLM analyzes formats and selects best quality
3. LLM calls download_video(url, format_id="best_format")
```

### Complex Site Analysis
```
1. LLM calls check_ytdlp_support(url) → fails
2. LLM calls analyze_webpage(url) → gets webpage info
3. LLM calls extract_media_patterns(url) → finds manifest URLs
4. LLM uses manifest URLs with download_video() or external tools
```

## 📦 Installation

```bash
# Install dependencies
pip install mcp yt-dlp requests aiohttp

# Make executable
chmod +x server.py
```

## 🔧 Usage

### With Claude Desktop
Add to your MCP configuration:

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

### With Other MCP Clients
The server communicates via stdin/stdout using the MCP protocol.

```bash
python server.py
```

## 🎭 LLM Usage Examples

**"Download this YouTube video in the best quality"**
```
→ check_ytdlp_support(url)
→ get_video_formats(url) 
→ download_video(url, format_id="best")
```

**"What video formats are available for this URL?"**
```
→ get_video_formats(url)
→ Returns formatted list of qualities, codecs, file sizes
```

**"This custom streaming site doesn't work with yt-dlp, can you analyze it?"**
```
→ check_ytdlp_support(url) → fails
→ analyze_webpage(url)
→ extract_media_patterns(url)
→ Returns manifest URLs and video files found
```

## 🔍 Comparison with Original Script

| Original Script | MCP Server |
|----------------|------------|
| **Monolithic workflow** | **Granular tools** |
| Fixed extraction order | LLM-orchestrated workflow |
| Built-in LLM analysis | LLM client does analysis |
| Single point of interaction | Multiple specialized tools |
| Limited extensibility | Highly composable |

## 🔒 Security Features

The MCP server includes comprehensive security protections:

- **Path traversal protection** - prevents `../` attacks
- **Configured download locations** - no arbitrary file access
- **Extension validation** - only safe file types allowed
- **Template sanitization** - removes dangerous shell characters
- **TOML configuration** - secure, no deserialization vulnerabilities

See [SECURITY.md](SECURITY.md) for detailed security documentation.

### Secure Download Example
```json
{
  "url": "https://example.com/video",
  "location_id": "default",          // Uses configured secure location
  "relative_path": "movies/action",  // Validated relative path
  "filename_template": "%(title)s.%(ext)s"  // Sanitized template
}
```

## 🛡️ Error Handling

Each tool returns structured JSON with:
- `success: boolean` - Operation status
- `error: string` - Error message if failed
- `data: object` - Tool-specific results

## 🔮 Benefits

1. **Intelligence Where It Matters**: LLMs decide strategy, not just content analysis
2. **Composable Workflows**: Tools can be combined in creative ways
3. **Fallback Flexibility**: Multiple analysis approaches available
4. **Client Agnostic**: Works with any MCP-compatible LLM client
5. **Efficient**: Only use expensive operations when needed

## 🏗️ Future Extensions

- **Playlist tools**: Handle playlists and channels
- **Format conversion**: Post-download processing
- **Batch operations**: Multiple URL processing
- **Custom extractors**: Site-specific extraction plugins
- **Caching layer**: Store analysis results

This MCP server transforms video downloading from a single-purpose script into a **flexible toolkit** that can be orchestrated intelligently by any LLM client!