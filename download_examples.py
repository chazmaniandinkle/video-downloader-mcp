#!/usr/bin/env python3
"""
Demonstration of download location and configuration options
"""

import os
import sys
sys.path.append('.')

from server import YtDlpExtractor

def demonstrate_download_paths():
    """Show different download path configurations"""
    
    print("🎬 Download Path Configuration Examples")
    print("=" * 60)
    
    # Test URL (we'll just analyze, not download)
    test_url = "https://www.facebook.com/reel/721818657509109"
    extractor = YtDlpExtractor()
    
    print("📋 Available configuration options for downloads:\n")
    
    # Example 1: Default behavior (no output_path specified)
    print("1️⃣ DEFAULT BEHAVIOR (no output_path specified):")
    print("   Command: download_video(url)")
    print("   Result: Downloads to CURRENT WORKING DIRECTORY")
    print("   Filename: yt-dlp's default naming (usually video title + format)")
    print(f"   Current directory: {os.getcwd()}")
    print("   Example filename: 'Video Title [abc123].mp4'\n")
    
    # Example 2: Specific directory
    print("2️⃣ SPECIFIC DIRECTORY:")
    print("   Command: download_video(url, output_path='/path/to/downloads/%(title)s.%(ext)s')")
    print("   Result: Downloads to specified directory")
    print("   Filename: Uses yt-dlp template variables")
    print("   Example: '/Users/username/Downloads/Video Title.mp4'\n")
    
    # Example 3: Template variables
    print("3️⃣ TEMPLATE VARIABLES (yt-dlp format):")
    template_examples = {
        "%(title)s.%(ext)s": "Video Title.mp4",
        "%(uploader)s - %(title)s.%(ext)s": "Channel Name - Video Title.mp4", 
        "%(upload_date)s - %(title)s.%(ext)s": "20250804 - Video Title.mp4",
        "%(uploader)s/%(title)s.%(ext)s": "Channel Name/Video Title.mp4",
        "downloads/%(resolution)s/%(title)s.%(ext)s": "downloads/1080p/Video Title.mp4"
    }
    
    for template, example in template_examples.items():
        print(f"   Template: {template}")
        print(f"   Result:   {example}")
        print()
    
    # Example 4: Fixed filename
    print("4️⃣ FIXED FILENAME:")
    print("   Command: download_video(url, output_path='/tmp/my_video.mp4')")
    print("   Result: Downloads with exact filename specified")
    print("   Note: Extension should match video format\n")
    
    # Example 5: Environment-based paths
    print("5️⃣ ENVIRONMENT-BASED PATHS:")
    home_dir = os.path.expanduser("~")
    downloads_dir = os.path.join(home_dir, "Downloads")
    print(f"   User home: {home_dir}")
    print(f"   Downloads: {downloads_dir}")
    print("   Command: download_video(url, output_path='~/Downloads/%(title)s.%(ext)s')")
    print("   Result: Downloads to user's Downloads folder\n")
    
    # Get actual info for demonstration
    print("6️⃣ REAL EXAMPLE with Facebook reel:")
    info = extractor.extract_info(test_url)
    if info:
        title = info.get('title', 'Unknown')
        ext = 'mp4'  # Most common
        
        print(f"   Video title: '{title}'")
        print("   Different output_path results:")
        print(f"     No output_path → ./{title}.{ext}")
        print(f"     '~/Downloads/%(title)s.%(ext)s' → ~/Downloads/{title}.{ext}")
        print(f"     '/tmp/facebook_reel.%(ext)s' → /tmp/facebook_reel.{ext}")
        print(f"     'videos/%(uploader)s/%(title)s.%(ext)s' → videos/{info.get('uploader', 'Unknown')}/{title}.{ext}")
    
    print("\n🛠️ IMPORTANT NOTES:")
    print("   • If output_path is not specified, downloads to current working directory")
    print("   • Template variables are processed by yt-dlp")
    print("   • Invalid characters in filenames are automatically cleaned")
    print("   • Directories are created automatically if they don't exist")
    print("   • File extensions are determined by the video format")
    
    print("\n📁 MCP Tool Interface:")
    print("   The download_video tool accepts:")
    print("   - url (required): Video URL to download")
    print("   - format_id (optional): Specific quality/format")
    print("   - output_path (optional): Where and how to save the file")
    
    print("\n🎯 Best Practices:")
    print("   • Always use absolute paths for predictable results")
    print("   • Use template variables for organized file naming")
    print("   • Consider using date/uploader folders for organization")
    print("   • Test with --simulate flag first for new configurations")

if __name__ == "__main__":
    demonstrate_download_paths()