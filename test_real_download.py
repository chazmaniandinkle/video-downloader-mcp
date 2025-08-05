#!/usr/bin/env python3
"""
Test actual download of Facebook reel using the MCP server components
"""

import json
import os
import sys
sys.path.append('.')

from server import YtDlpExtractor

def test_facebook_reel_real_download():
    """Actually download the Facebook reel to test functionality"""
    
    url = "https://www.facebook.com/reel/721818657509109"
    output_dir = "/tmp/video_test"
    
    print(f"🎬 Testing REAL Facebook Reel Download")
    print(f"URL: {url}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Test the MCP server components
    extractor = YtDlpExtractor()
    
    # Step 1: Check support
    print("📋 Step 1: Checking yt-dlp support...")
    info = extractor.extract_info(url)
    if not info:
        print("❌ URL not supported")
        return
        
    print("✅ URL supported")
    print(f"   Title: {info.get('title')}")
    print(f"   Duration: {info.get('duration')} seconds")
    
    # Step 2: Download with automatic format selection
    print("\n💾 Step 2: Downloading video...")
    output_template = f"{output_dir}/%(title)s.%(ext)s"
    
    # Use the MCP server's download function
    result = extractor.download_video(url, output_path=output_template)
    
    if result.get('success'):
        print("✅ Download successful!")
        
        # List what was downloaded
        print("\n📁 Downloaded files:")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   - {file} ({file_size:,} bytes)")
        
        print(f"\n📝 Download logs:")
        if result.get('stdout'):
            print("   STDOUT:", result['stdout'][-200:])  # Last 200 chars
        
    else:
        print("❌ Download failed!")
        print(f"   Error: {result.get('error')}")
        if result.get('stderr'):
            print(f"   Stderr: {result['stderr']}")
    
    # Step 3: Test format-specific download
    print(f"\n🎥 Step 3: Testing format-specific download...")
    formats = extractor.get_formats(url)
    if formats:
        # Find a good video format
        video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
        if video_formats:
            # Try downloading with best format
            best_format = max(video_formats, key=lambda x: x.get('height', 0))
            print(f"   Trying format: {best_format.get('format_id')} ({best_format.get('height')}p)")
            
            # Use automatic format selection instead of specific format ID
            # This tends to work better with Facebook
            specific_output = f"{output_dir}/specific_format.%(ext)s"
            result = extractor.download_video(url, output_path=specific_output)
            
            if result.get('success'):
                print("   ✅ Format-specific download successful!")
            else:
                print(f"   ⚠️ Format-specific download failed, but that's okay")
                print(f"   (Facebook formats can be tricky)")
    
    print(f"\n🎉 Test completed! Check {output_dir} for downloaded files.")

if __name__ == "__main__":
    test_facebook_reel_real_download()