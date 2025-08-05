#!/usr/bin/env python3
"""
Simple test to download the Facebook reel using the MCP server tools directly
"""

import json
import sys
import os
sys.path.append('.')

from server import YtDlpExtractor, WebpageAnalyzer

def test_facebook_reel_download():
    """Test downloading the Facebook reel"""
    
    url = "https://www.facebook.com/reel/721818657509109"
    print(f"🎬 Testing Facebook Reel Download: {url}")
    print("=" * 60)
    
    # Test 1: Check if URL is supported
    print("📋 Step 1: Checking yt-dlp support...")
    extractor = YtDlpExtractor()
    
    if not extractor.check_availability():
        print("❌ yt-dlp not available")
        return
    
    info = extractor.extract_info(url)
    if info:
        print("✅ URL supported by yt-dlp")
        print(f"   Title: {info.get('title')}")
        print(f"   Duration: {info.get('duration')} seconds")
        print(f"   Uploader: {info.get('uploader')}")
    else:
        print("❌ URL not supported by yt-dlp")
        return
    
    # Test 2: Get available formats
    print("\n🎥 Step 2: Getting available formats...")
    formats = extractor.get_formats(url)
    if formats:
        print(f"✅ Found {len(formats)} formats")
        print("   Top formats:")
        for i, fmt in enumerate(formats[:5]):  # Show top 5
            resolution = f"{fmt.get('height', 'unknown')}p" if fmt.get('height') else 'audio-only'
            print(f"     {i+1}. ID: {fmt.get('format_id')} | {resolution} | {fmt.get('ext')} | {fmt.get('vcodec', 'unknown')}")
    else:
        print("❌ Could not get formats")
        return
    
    # Test 3: Download video (analyze only - don't actually download)
    print("\n💾 Step 3: Testing download preparation...")
    
    # Find best video format
    video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
    if video_formats:
        # Sort by height (resolution) descending
        best_format = max(video_formats, key=lambda x: x.get('height', 0))
        print(f"   Best format: {best_format.get('format_id')} ({best_format.get('height')}p)")
        
        # Simulate download call (without actually downloading)
        print(f"   Would download with format ID: {best_format.get('format_id')}")
        print(f"   Output would be: {info.get('title', 'video')}.{best_format.get('ext')}")
        
        # Actually test the download function but with --simulate
        print("\n🧪 Step 4: Testing download function (simulation)...")
        import subprocess
        cmd = ["yt-dlp", "--simulate", "-f", best_format.get('format_id'), url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Download simulation successful")
            print("   Command would succeed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Download simulation failed: {e}")
            print(f"   Stderr: {e.stderr}")
    else:
        print("❌ No suitable video formats found")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_facebook_reel_download()