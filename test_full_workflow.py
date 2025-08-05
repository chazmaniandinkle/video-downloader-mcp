#!/usr/bin/env python3
"""
Test the complete MCP server workflow with a real video
"""

import sys
import json
import asyncio
import os

sys.path.append('.')
from server import handle_call_tool

async def test_complete_workflow():
    """Test full workflow from check to download"""
    print("🎬 Testing Complete Video Downloader Workflow")
    print("=" * 55)
    
    # Use a short YouTube video for testing
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll (short)
    
    print(f"🎯 Target URL: {test_url}")
    print()
    
    # Step 1: Check if supported
    print("1️⃣ Checking yt-dlp support...")
    try:
        result = await handle_call_tool("check_ytdlp_support", {"url": test_url})
        response = json.loads(result[0].text)
        
        if response.get("supported"):
            print("✅ URL is supported by yt-dlp")
            print(f"   Title: {response.get('title', 'N/A')}")
            print(f"   Duration: {response.get('duration', 'N/A')} seconds")
            print(f"   Uploader: {response.get('uploader', 'N/A')}")
        else:
            print(f"❌ URL not supported: {response.get('error')}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    print()
    
    # Step 2: Get download locations
    print("2️⃣ Getting available download locations...")
    try:
        result = await handle_call_tool("get_download_locations", {})
        response = json.loads(result[0].text)
        
        if response.get("success"):
            print("✅ Download locations retrieved")
            for location_id, info in response["locations"].items():
                status = "✓ writable" if info["writable"] else "✗ not writable"
                print(f"   {location_id}: {info['original']} ({status})")
        else:
            print(f"❌ Failed: {response.get('error')}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    print()
    
    # Step 3: Get video info and formats
    print("3️⃣ Getting video information...")
    try:
        result = await handle_call_tool("get_video_info", {"url": test_url})
        response = json.loads(result[0].text)
        
        if response.get("success"):
            print("✅ Video information retrieved")
            print(f"   Title: {response.get('title', 'N/A')}")
            print(f"   Duration: {response.get('duration', 'N/A')} seconds")
            print(f"   Available formats: {response.get('format_count', 'N/A')}")
            print(f"   Subtitle languages: {len(response.get('subtitle_languages', []))}")
        else:
            print(f"❌ Failed: {response.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Step 4: Get formats (limited output for readability)
    print("4️⃣ Getting video formats...")
    try:
        result = await handle_call_tool("get_video_formats", {"url": test_url})
        response = json.loads(result[0].text)
        
        if response.get("success"):
            formats = response["formats"]
            print(f"✅ Found {len(formats)} formats")
            
            # Show a few interesting formats
            video_formats = [f for f in formats if f.get('vcodec') != 'none'][:3]
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none'][:2]
            
            print("   Sample video formats:")
            for fmt in video_formats:
                print(f"   - {fmt['format_id']}: {fmt['resolution']} {fmt['ext']} ({fmt.get('format_note', 'N/A')})")
            
            print("   Sample audio formats:")
            for fmt in audio_formats:
                print(f"   - {fmt['format_id']}: {fmt['ext']} audio-only ({fmt.get('format_note', 'N/A')})")
        else:
            print(f"❌ Failed: {response.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Step 5: Secure download test (audio only to be quick)
    print("5️⃣ Testing secure download (audio-only for speed)...")
    try:
        result = await handle_call_tool("download_video", {
            "url": test_url,
            "location_id": "default",
            "relative_path": "test_workflow",
            "filename_template": "test_audio.%(ext)s",
            "format_id": "140"  # Usually m4a audio
        })
        
        response = json.loads(result[0].text)
        if response.get("success"):
            print("✅ Secure download successful!")
            download_path = response.get("download_path")
            print(f"   Path: {download_path}")
            
            # Check if file exists and get size
            if download_path and os.path.exists(download_path):
                size = os.path.getsize(download_path)
                print(f"   File size: {size:,} bytes")
                print(f"   File exists: ✅")
            else:
                print("   File not found at expected path (may be template)")
        else:
            print(f"❌ Download failed: {response.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Step 6: Test security validation
    print("6️⃣ Testing security protections...")
    
    security_tests = [
        {
            "name": "Path traversal protection",
            "args": {
                "url": test_url,
                "location_id": "default", 
                "relative_path": "../../../etc/passwd"
            },
            "expect_success": False
        },
        {
            "name": "Invalid location blocking",
            "args": {
                "url": test_url,
                "location_id": "hacker_location"
            },
            "expect_success": False
        }
    ]
    
    for test in security_tests:
        print(f"   🛡️  {test['name']}:")
        try:
            result = await handle_call_tool("download_video", test["args"])
            response = json.loads(result[0].text)
            
            success = response.get("success", False)
            if success == test["expect_success"]:
                status = "✅ Allowed" if success else "🛡️  Blocked"
                print(f"      {status}: {response.get('download_path', response.get('error'))}")
            else:
                print(f"      ❌ Unexpected result: success={success}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print()
    print("🎉 Complete workflow test finished!")

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())