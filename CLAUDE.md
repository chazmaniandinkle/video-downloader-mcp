# CLAUDE.md

This file provides guidance to Claude Code when working with the Video Downloader MCP Server project.

## Project Overview

This MCP server exposes video downloading capabilities as discrete tools that LLMs can orchestrate intelligently. It represents a **paradigm shift** from the original monolithic script to a **tool-based architecture**.

## Architecture Philosophy

### **Tool-First Design**
- Each operation is a discrete tool with clear input/output
- LLMs make intelligent decisions about tool usage
- Granular control enables complex workflows
- Error handling is structured and actionable

### **Layered Fallback Strategy**
1. **Primary**: yt-dlp tools (fast, comprehensive)
2. **Fallback**: Webpage analysis tools (pattern matching)
3. **Future**: Custom extraction plugins

### **LLM as Orchestrator**
- LLM clients decide which tools to use and when
- Tools provide structured data for LLM decision-making
- Complex workflows emerge from simple tool combinations

## Core Components

### **YtDlpExtractor Class**
- Wraps yt-dlp functionality in clean Python interfaces
- Provides structured error handling
- Formats output for LLM consumption
- Methods:
  - `check_availability()`: System check
  - `extract_info()`: Full video metadata
  - `get_formats()`: Available quality options
  - `download_video()`: Actual download execution

### **WebpageAnalyzer Class**
- Fallback analysis for unsupported sites
- Pattern matching for media URLs
- Metadata extraction from HTML
- Methods:
  - `fetch_page_source()`: HTTP request handling
  - `extract_video_patterns()`: Regex-based URL extraction
  - `extract_metadata()`: Title, duration, etc.

### **MCP Tool Definitions**
Each tool follows MCP specification:
- Clear name and description
- JSON Schema input validation
- Structured JSON output
- Error handling with meaningful messages

## Tool Interface Design

### **Input Patterns**
```python
# Simple URL input
{"url": "https://example.com/video"}

# Complex operations
{
    "url": "https://example.com/video",
    "format_id": "137",  # optional
    "output_path": "%(title)s.%(ext)s"  # optional
}
```

### **Output Patterns**
```python
# Success response
{
    "success": True,
    "title": "Video Title",
    "formats": [...],
    # ... other data
}

# Error response
{
    "success": False,
    "error": "Detailed error message"
}
```

## Development Guidelines

### **Adding New Tools**
1. Define tool in `handle_list_tools()`
2. Implement logic in `handle_call_tool()`
3. Follow input/output patterns
4. Add comprehensive error handling
5. Update documentation

### **Tool Design Principles**
- **Single Responsibility**: Each tool does one thing well
- **Idempotent**: Same input produces same output
- **Structured Output**: Always return JSON with consistent schema
- **Error Transparency**: Clear error messages for debugging
- **LLM Friendly**: Output designed for LLM interpretation

### **Error Handling Strategy**
```python
# Always return structured responses
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

## Integration Patterns

### **MCP Client Configuration**
```json
{
  "mcpServers": {
    "video-downloader": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

### **Common LLM workflows**

**Quality-aware downloading**:
```
1. check_ytdlp_support() → confirm support
2. get_video_formats() → analyze options
3. download_video(format_id=best) → execute
```

**Fallback analysis**:
```
1. check_ytdlp_support() → fails
2. analyze_webpage() → understand structure  
3. extract_media_patterns() → find URLs
4. [LLM processes results for next steps]
```

## Testing Strategy

### **Unit Testing**
- Mock yt-dlp subprocess calls
- Test error conditions
- Validate JSON schema compliance
- Test regex patterns with sample HTML

### **Integration Testing**
- Test with real URLs (YouTube, Facebook, etc.)
- Verify MCP protocol compliance
- Test with actual LLM clients
- Performance testing with large playlists

### **Test Data**
- Sample HTML files with various video player types
- Mock yt-dlp responses for consistent testing
- Test URLs across different site types

## Performance Considerations

### **Caching Strategy**
- Consider caching yt-dlp info extraction
- Cache webpage content for repeated analysis
- Implement TTL for cached data

### **Resource Management**
- Timeout handling for long-running operations
- Memory management for large video files
- Concurrent request limiting

### **Optimization Opportunities**
- Parallel format checking
- Streaming download progress reporting
- Incremental metadata extraction

## Security Considerations

### **Input Validation**
- URL validation and sanitization
- Path traversal prevention in output paths
- Resource limits for downloads

### **Subprocess Safety**
- Proper command escaping
- Timeout enforcement
- Resource limits

## Future Extensions

### **Planned Features**
1. **Playlist Tools**: Handle YouTube playlists, channels
2. **Format Conversion**: Post-download processing
3. **Batch Operations**: Multiple URL processing
4. **Progress Reporting**: Real-time download status
5. **Custom Extractors**: Site-specific plugins

### **Advanced Integrations**
- **Database Storage**: Metadata persistence
- **Queue Management**: Background download processing
- **Notification Systems**: Completion alerts
- **Analytics**: Usage tracking and optimization

## Dependencies

### **Core Requirements**
- `mcp>=0.2.0`: MCP protocol implementation
- `yt-dlp>=2023.1.6`: Video extraction engine
- `requests>=2.28.0`: HTTP client
- `aiohttp>=3.8.0`: Async HTTP for future features

### **Development Dependencies**
- `black`: Code formatting
- `isort`: Import sorting
- `mypy`: Type checking
- `pytest`: Testing framework

## Troubleshooting

### **Common Issues**
- **yt-dlp not found**: Ensure yt-dlp is installed and in PATH
- **MCP connection fails**: Check stdin/stdout setup
- **Downloads fail**: Verify output directory permissions
- **Pattern extraction empty**: Site may use dynamic loading

### **Debug Mode**
Enable verbose logging by setting environment variables:
```bash
export MCP_DEBUG=1
export YTDLP_DEBUG=1
python server.py
```

This MCP server represents a **modern, composable approach** to video downloading that leverages LLM intelligence for workflow orchestration while maintaining the power and reliability of yt-dlp for actual extraction.