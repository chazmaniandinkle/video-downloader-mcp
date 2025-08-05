#!/usr/bin/env python3
"""
Test MCP server functionality by simulating tool calls
"""

import json
import asyncio
import sys
sys.path.append('.')

from server import server, YtDlpExtractor
import mcp.types as types

async def test_mcp_tools():
    """Test the MCP server tools directly"""
    
    print("🧪 Testing MCP Server Tools")
    print("=" * 40)
    
    # Test 1: List tools
    print("📋 Test 1: List available tools")
    tools = await server.list_tools()
    print(f"   Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    # Test 2: Check yt-dlp support for Facebook reel
    print(f"\n🔍 Test 2: Check Facebook reel support")
    url = "https://www.facebook.com/reel/721818657509109"
    
    result = await server.call_tool("check_ytdlp_support", {"url": url})
    response_data = json.loads(result[0].text)
    print(f"   Supported: {response_data.get('supported')}")
    if response_data.get('supported'):
        print(f"   Title: {response_data.get('title')}")
        print(f"   Duration: {response_data.get('duration')} seconds")
    
    # Test 3: Get video info
    print(f"\n📊 Test 3: Get detailed video info")
    result = await server.call_tool("get_video_info", {"url": url})
    response_data = json.loads(result[0].text)
    if response_data.get('success'):
        print(f"   ✅ Success")
        print(f"   Title: {response_data.get('title')}")
        print(f"   Uploader: {response_data.get('uploader')}")
        print(f"   Duration: {response_data.get('duration')} seconds")
        print(f"   Format count: {response_data.get('format_count')}")
    else:
        print(f"   ❌ Failed: {response_data.get('error')}")
    
    # Test 4: Get formats
    print(f"\n🎥 Test 4: Get available formats")
    result = await server.call_tool("get_video_formats", {"url": url})
    response_data = json.loads(result[0].text)
    if response_data.get('success'):
        formats = response_data.get('formats', [])
        print(f"   ✅ Found {len(formats)} formats")
        
        # Show video formats
        video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('resolution') != 'audio-only']
        print(f"   Video formats: {len(video_formats)}")
        for fmt in video_formats[:3]:  # Show top 3
            print(f"     - {fmt.get('format_id')}: {fmt.get('resolution')} {fmt.get('ext')} ({fmt.get('vcodec')})")
        
        # Show audio formats
        audio_formats = [f for f in formats if f.get('resolution') == 'audio-only']
        print(f"   Audio formats: {len(audio_formats)}")
        for fmt in audio_formats[:2]:  # Show top 2
            print(f"     - {fmt.get('format_id')}: {fmt.get('ext')} ({fmt.get('acodec')})")
    else:
        print(f"   ❌ Failed: {response_data.get('error')}")
    
    # Test 5: Simulate download (without actually downloading)
    print(f"\n💾 Test 5: Simulate download")
    
    # Use automatic format selection (no format_id specified)
    # This should work better than specifying exact format IDs
    result = await server.call_tool("download_video", {
        "url": url,
        "output_path": "/tmp/test_video.%(ext)s"  # Safe test location
    })
    response_data = json.loads(result[0].text)
    
    print(f"   Download simulation:")
    print(f"   Success: {response_data.get('success')}")
    if not response_data.get('success'):
        print(f"   Error: {response_data.get('error')}")
    else:
        print(f"   Would download to: /tmp/test_video.*")
    
    # Test 6: Test fallback functionality
    print(f"\n🔧 Test 6: Test fallback analysis on unsupported site")
    test_url = "https://httpbin.org/html"  # Simple test site
    
    result = await server.call_tool("analyze_webpage", {"url": test_url})
    response_data = json.loads(result[0].text)
    if response_data.get('success'):
        print(f"   ✅ Webpage analysis successful")
        print(f"   Content length: {response_data.get('content_length')} chars")
        print(f"   Has video tags: {response_data.get('has_video_tags')}")
        print(f"   Has iframes: {response_data.get('has_iframe')}")
    else:
        print(f"   ❌ Failed: {response_data.get('error')}")
    
    print(f"\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())