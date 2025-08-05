#!/usr/bin/env python3
"""
Test a real download with actual file creation
"""

import sys
import json
import asyncio
import os
from pathlib import Path

sys.path.append('.')
from server import handle_call_tool

async def test_real_download():
    """Test actual download with file creation"""
    print("📥 Testing Real Download with File Creation")
    print("=" * 50)
    
    # Use a very short YouTube video
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Create download directory
    download_dir = Path.home() / "video-downloader" / "test_real"
    download_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Download directory: {download_dir}")
    print()
    
    # Test download with explicit template expansion
    print("🎯 Downloading audio with explicit filename...")
    try:
        result = await handle_call_tool("download_video", {
            "url": test_url,
            "location_id": "default",
            "relative_path": "test_real",
            "filename_template": "rick_astley_test.%(ext)s",
            "format_id": "140"  # m4a audio format
        })
        
        response = json.loads(result[0].text)
        print(f"Response: {response}")
        
        if response.get("success"):
            print("✅ Download successful!")
            download_path = response.get("download_path")
            print(f"   Reported path: {download_path}")
            
            # Check the directory for any files
            print(f"\n📂 Checking download directory contents:")
            if download_dir.exists():
                files = list(download_dir.glob("*"))
                if files:
                    for file_path in files:
                        if file_path.is_file():
                            size = file_path.stat().st_size
                            print(f"   📄 {file_path.name} ({size:,} bytes)")
                else:
                    print("   (No files found)")
            
            # Also check if any yt-dlp created files in current directory
            print(f"\n📂 Checking current directory for any yt-dlp files:")
            current_files = [f for f in os.listdir('.') if 'rick' in f.lower() or 'astley' in f.lower()]
            for file in current_files:
                if os.path.isfile(file):
                    size = os.path.getsize(file)
                    print(f"   📄 {file} ({size:,} bytes)")
                    
        else:
            print(f"❌ Download failed: {response.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("📊 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_real_download())