#!/usr/bin/env python3
"""
Video Downloader MCP Server

Exposes video downloading and analysis capabilities as MCP tools, allowing
LLMs to intelligently orchestrate video extraction workflows.
"""

import asyncio
import json
import subprocess
import requests
import re
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python versions

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureConfigManager:
    """Manages secure configuration loading from TOML files"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default to user's config directory
            config_dir = Path.home() / ".config" / "video-downloader-mcp"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.toml"
        else:
            self.config_path = Path(config_path)
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file with secure defaults"""
        default_config = {
            "download_locations": {
                "default": "~/video-downloader"
            },
            "security": {
                "enforce_location_restrictions": True,
                "max_filename_length": 255,
                "allowed_extensions": ["mp4", "webm", "mkv", "avi", "mov", "m4a", "mp3", "aac", "ogg", "wav", "vtt", "srt", "ass", "ssa"],
                "block_path_traversal": True
            },
            "ytdlp": {
                "default_format": "best[height<=1080]",
                "default_filename_template": "%(title)s.%(ext)s",
                "max_download_size": 0
            },
            "logging": {
                "log_security_events": True,
                "log_downloads": True
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, "rb") as f:
                    user_config = tomllib.load(f)
                # Deep merge user config with defaults
                return self._deep_merge(default_config, user_config)
            except Exception as e:
                logger.error(f"Error loading config from {self.config_path}: {e}")
                logger.info("Using default configuration")
                return default_config
        else:
            # Create default config file
            self._create_default_config()
            return default_config
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _create_default_config(self):
        """Create default configuration file"""
        try:
            # Copy the bundled config.toml as a template
            script_dir = Path(__file__).parent
            template_config = script_dir / "config.toml"
            
            if template_config.exists():
                import shutil
                shutil.copy2(template_config, self.config_path)
                logger.info(f"Created default configuration at {self.config_path}")
            else:
                logger.warning("Template config.toml not found, using built-in defaults")
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
    
    def get(self, path: str, default=None):
        """Get config value using dot notation"""
        keys = path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

class PathValidator:
    """Validates and sanitizes file paths for security"""
    
    def __init__(self, config: SecureConfigManager):
        self.config = config
        self.allowed_extensions = set(config.get('security.allowed_extensions', []))
        self.max_filename_length = config.get('security.max_filename_length', 255)
        self.block_traversal = config.get('security.block_path_traversal', True)
    
    def validate_path(self, path: str, base_dir: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Validate a path against security constraints
        Returns: (is_valid, normalized_path, error_message)
        """
        try:
            # Check for path traversal attempts
            if self.block_traversal and self._contains_traversal(path):
                return False, None, "Path traversal sequences detected"
            
            # Expand user home directory
            base_dir = os.path.expanduser(base_dir)
            
            # Handle relative paths
            if not os.path.isabs(path):
                full_path = os.path.join(base_dir, path)
            else:
                return False, None, "Absolute paths not allowed"
            
            # Normalize and resolve the path
            normalized = os.path.realpath(full_path)
            base_real = os.path.realpath(base_dir)
            
            # Ensure the path stays within the base directory
            if not normalized.startswith(base_real + os.sep) and normalized != base_real:
                return False, None, f"Path escapes allowed directory: {base_dir}"
            
            # Validate filename length
            filename = os.path.basename(normalized)
            if len(filename) > self.max_filename_length:
                return False, None, f"Filename too long (max {self.max_filename_length} chars)"
            
            # Validate file extension if specified
            if self.allowed_extensions:
                ext = os.path.splitext(filename)[1].lower().lstrip('.')
                if ext and ext not in self.allowed_extensions:
                    return False, None, f"File extension .{ext} not allowed"
            
            return True, normalized, None
            
        except Exception as e:
            return False, None, f"Path validation error: {str(e)}"
    
    def _contains_traversal(self, path: str) -> bool:
        """Check if path contains traversal sequences"""
        dangerous_patterns = ['../', '..\\', '..\\\\', '..//']
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in dangerous_patterns)
    
    def sanitize_template_vars(self, template: str) -> str:
        """Sanitize yt-dlp template variables to prevent injection"""
        # Remove potentially dangerous characters from template
        dangerous_chars = ['|', '&', ';', '$', '`', '>', '<']
        sanitized = template
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        return sanitized

class LocationManager:
    """Manages configured download locations"""
    
    def __init__(self, config: SecureConfigManager):
        self.config = config
        self.validator = PathValidator(config)
        self._locations_cache = None
    
    def get_locations(self) -> Dict[str, Dict[str, str]]:
        """Get all configured download locations with metadata"""
        if self._locations_cache is None:
            self._locations_cache = self._build_locations()
        return self._locations_cache
    
    def _build_locations(self) -> Dict[str, Dict[str, str]]:
        """Build locations dictionary with validation"""
        locations = {}
        configured_locations = self.config.get('download_locations', {})
        
        for location_id, path in configured_locations.items():
            expanded_path = os.path.expanduser(path)
            
            # Create directory if it doesn't exist
            try:
                os.makedirs(expanded_path, mode=0o755, exist_ok=True)
                
                # Verify we can write to it
                if os.access(expanded_path, os.W_OK):
                    locations[location_id] = {
                        "path": expanded_path,
                        "original": path,
                        "writable": True,
                        "description": f"Download location: {path}"
                    }
                else:
                    logger.warning(f"Location {location_id} ({path}) is not writable")
                    locations[location_id] = {
                        "path": expanded_path,
                        "original": path,
                        "writable": False,
                        "description": f"Download location: {path} (not writable)"
                    }
                    
            except Exception as e:
                logger.error(f"Failed to create/access location {location_id} ({path}): {e}")
                locations[location_id] = {
                    "path": expanded_path,
                    "original": path,
                    "writable": False,
                    "description": f"Download location: {path} (error: {str(e)})"
                }
        
        return locations
    
    def validate_location(self, location_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Validate a location ID
        Returns: (is_valid, path, error_message)
        """
        locations = self.get_locations()
        
        if location_id not in locations:
            available = list(locations.keys())
            return False, None, f"Unknown location '{location_id}'. Available: {available}"
        
        location = locations[location_id]
        if not location["writable"]:
            return False, None, f"Location '{location_id}' is not writable"
        
        return True, location["path"], None
    
    def construct_download_path(self, location_id: str, relative_path: Optional[str] = None, 
                              filename_template: Optional[str] = None) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Construct a secure download path
        Returns: (is_valid, full_path, error_message)
        """
        # Validate location
        valid, base_path, error = self.validate_location(location_id)
        if not valid:
            return False, None, error
        
        # Construct relative path
        if relative_path:
            # Sanitize the relative path
            if filename_template:
                # If template is provided, combine them
                full_relative = os.path.join(relative_path, filename_template)
            else:
                full_relative = relative_path
        elif filename_template:
            full_relative = filename_template
        else:
            # Use default template
            full_relative = self.config.get('ytdlp.default_filename_template', '%(title)s.%(ext)s')
        
        # Sanitize template variables
        full_relative = self.validator.sanitize_template_vars(full_relative)
        
        # Validate the final path
        return self.validator.validate_path(full_relative, base_path)

# Server instance
server = Server("video-downloader")

@dataclass
class VideoInfo:
    """Structured video information"""
    title: str
    duration: Optional[int]
    thumbnail: Optional[str]
    description: Optional[str]
    uploader: Optional[str]
    upload_date: Optional[str]
    view_count: Optional[int]
    formats: List[Dict[str, Any]]
    subtitles: Dict[str, List[Dict[str, str]]]
    webpage_url: str

class YtDlpExtractor:
    """yt-dlp extraction wrapper"""
    
    @staticmethod
    def check_availability() -> bool:
        """Check if yt-dlp is available"""
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def extract_info(url: str, extract_flat: bool = False) -> Optional[Dict[str, Any]]:
        """Extract video information using yt-dlp"""
        try:
            cmd = ["yt-dlp", "-J", "--no-warnings"]
            if extract_flat:
                cmd.append("--flat-playlist")
            cmd.append(url)
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            return json.loads(result.stdout)
        except Exception:
            return None
    
    @staticmethod
    def get_formats(url: str) -> Optional[List[Dict[str, Any]]]:
        """Get available formats for a video"""
        info = YtDlpExtractor.extract_info(url)
        if info and 'formats' in info:
            return info['formats']
        return None
    
    @staticmethod
    def download_video(url: str, format_id: Optional[str] = None, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Download video using yt-dlp"""
        cmd = ["yt-dlp"]
        
        if format_id:
            cmd.extend(["-f", format_id])
        
        if output_path:
            cmd.extend(["-o", output_path])
        
        cmd.append(url)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": e.stdout,
                "stderr": e.stderr
            }

class WebpageAnalyzer:
    """Fallback webpage analysis for unsupported sites"""
    
    @staticmethod
    def fetch_page_source(url: str) -> Optional[str]:
        """Fetch webpage source code"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception:
            return None
    
    @staticmethod
    def extract_video_patterns(html_content: str, base_url: str) -> Dict[str, List[str]]:
        """Extract potential video/audio/subtitle URLs using regex patterns"""
        patterns = {
            'mpd_manifests': [
                r'(["\'])(https?://[^"\']*\.mpd(?:\?[^"\']*)?)\1',
                r'manifest["\']:\s*["\']([^"\']*\.mpd(?:\?[^"\']*)?)["\']',
            ],
            'm3u8_playlists': [
                r'(["\'])(https?://[^"\']*\.m3u8(?:\?[^"\']*)?)\1',
                r'playlist["\']:\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            ],
            'video_files': [
                r'(["\'])(https?://[^"\']*\.(?:mp4|webm|mkv|avi|mov)(?:\?[^"\']*)?)\1',
                r'src["\']:\s*["\']([^"\']*\.(?:mp4|webm|mkv)(?:\?[^"\']*)?)["\']',
            ],
            'audio_files': [
                r'(["\'])(https?://[^"\']*\.(?:mp3|m4a|aac|ogg|wav)(?:\?[^"\']*)?)\1',
            ],
            'subtitle_files': [
                r'(["\'])(https?://[^"\']*\.(?:vtt|srt|ass|ssa)(?:\?[^"\']*)?)\1',
            ]
        }
        
        extracted = {}
        
        for category, pattern_list in patterns.items():
            extracted[category] = []
            for pattern in pattern_list:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    # Handle different regex group patterns
                    url = match[1] if isinstance(match, tuple) and len(match) > 1 else match
                    if isinstance(url, tuple):
                        url = url[0] if url[0] else url[1]
                    
                    # Convert relative URLs to absolute
                    if url.startswith('//'):
                        url = f"https:{url}"
                    elif url.startswith('/'):
                        url = urljoin(base_url, url)
                    elif not url.startswith('http'):
                        url = urljoin(base_url, url)
                    
                    if url not in extracted[category]:
                        extracted[category].append(url)
        
        return extracted
    
    @staticmethod
    def extract_metadata(html_content: str) -> Dict[str, str]:
        """Extract video metadata from HTML"""
        metadata = {}
        
        # Title extraction patterns
        title_patterns = [
            r'<title[^>]*>([^<]+)</title>',
            r'["\']title["\']:\s*["\']([^"\']+)["\']',
            r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                metadata['title'] = match.group(1).strip()
                break
        
        # Duration extraction
        duration_patterns = [
            r'duration["\']:\s*["\']?(\d+)["\']?',
            r'["\']duration["\']:\s*(\d+)',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                metadata['duration'] = int(match.group(1))
                break
        
        return metadata

# MCP Tool Definitions

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available video downloader tools"""
    return [
        types.Tool(
            name="check_ytdlp_support",
            description="Check if a URL is supported by yt-dlp and get basic info",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Video URL to check"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="get_video_info",
            description="Get detailed video information including available formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Video URL to analyze"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="get_video_formats",
            description="Get available video/audio formats and quality options",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Video URL to get formats for"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="download_video",
            description="Download video with specified format and output options",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Video URL to download"
                    },
                    "format_id": {
                        "type": "string",
                        "description": "Specific format ID to download (optional)"
                    },
                    "output_path": {
                        "type": "string", 
                        "description": "Output file path template (optional)"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="analyze_webpage",
            description="Fallback: Analyze webpage for video content when yt-dlp fails",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Webpage URL to analyze"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="extract_media_patterns",
            description="Extract video/audio URLs from webpage HTML using pattern matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Webpage URL to extract media from"
                    }
                },
                "required": ["url"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if name == "check_ytdlp_support":
        url = arguments["url"]
        
        if not YtDlpExtractor.check_availability():
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "supported": False,
                    "error": "yt-dlp is not installed or available"
                })
            )]
        
        info = YtDlpExtractor.extract_info(url)
        if info:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "supported": True,
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader"),
                    "view_count": info.get("view_count"),
                    "upload_date": info.get("upload_date"),
                    "description": info.get("description", "")[:200] + "..." if info.get("description") else None
                })
            )]
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "supported": False,
                    "error": "URL not supported by yt-dlp"
                })
            )]
    
    elif name == "get_video_info":
        url = arguments["url"]
        info = YtDlpExtractor.extract_info(url)
        
        if not info:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Could not extract video information"
                })
            )]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "title": info.get("title"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "description": info.get("description"),
                "uploader": info.get("uploader"),
                "upload_date": info.get("upload_date"),
                "view_count": info.get("view_count"),
                "webpage_url": info.get("webpage_url"),
                "format_count": len(info.get("formats", [])),
                "subtitle_languages": list(info.get("subtitles", {}).keys())
            })
        )]
    
    elif name == "get_video_formats":
        url = arguments["url"]
        formats = YtDlpExtractor.get_formats(url)
        
        if not formats:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Could not get video formats"
                })
            )]
        
        # Process formats for easier consumption
        processed_formats = []
        for fmt in formats:
            processed_formats.append({
                "format_id": fmt.get("format_id"),
                "ext": fmt.get("ext"),
                "resolution": f"{fmt.get('height', 'unknown')}p" if fmt.get('height') else 'audio-only',
                "fps": fmt.get("fps"),
                "vcodec": fmt.get("vcodec"),
                "acodec": fmt.get("acodec"),
                "filesize": fmt.get("filesize"),
                "tbr": fmt.get("tbr"),
                "format_note": fmt.get("format_note"),
                "url": fmt.get("url", "")[:100] + "..." if fmt.get("url") else None
            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "formats": processed_formats
            })
        )]
    
    elif name == "download_video":
        url = arguments["url"]
        format_id = arguments.get("format_id")
        output_path = arguments.get("output_path")
        
        result = YtDlpExtractor.download_video(url, format_id, output_path)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result)
        )]
    
    elif name == "analyze_webpage":
        url = arguments["url"]
        
        html_content = WebpageAnalyzer.fetch_page_source(url)
        if not html_content:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Could not fetch webpage content"
                })
            )]
        
        metadata = WebpageAnalyzer.extract_metadata(html_content)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "metadata": metadata,
                "content_length": len(html_content),
                "has_video_tags": "<video" in html_content.lower(),
                "has_iframe": "<iframe" in html_content.lower()
            })
        )]
    
    elif name == "extract_media_patterns":
        url = arguments["url"]
        
        html_content = WebpageAnalyzer.fetch_page_source(url)
        if not html_content:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Could not fetch webpage content"
                })
            )]
        
        patterns = WebpageAnalyzer.extract_video_patterns(html_content, url)
        metadata = WebpageAnalyzer.extract_metadata(html_content)
        
        total_found = sum(len(urls) for urls in patterns.values())
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "total_media_urls": total_found,
                "patterns": patterns,
                "metadata": metadata
            })
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="video-downloader",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())