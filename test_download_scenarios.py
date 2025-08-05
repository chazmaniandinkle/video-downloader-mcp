#!/usr/bin/env python3
"""
Test different download scenarios to show where files go
"""

import os
import json
import sys
sys.path.append('.')

from server import YtDlpExtractor

def test_download_scenarios():
    """Test different download configurations"""
    
    print("🎯 Testing Download Scenarios")
    print("=" * 50)
    
    test_url = "https://www.facebook.com/reel/721818657509109"
    extractor = YtDlpExtractor()
    
    # Create test directories
    test_dirs = {
        "downloads": "/tmp/test_downloads",
        "organized": "/tmp/organized_videos", 
        "user_downloads": os.path.expanduser("~/Downloads/video_test")
    }
    
    for name, path in test_dirs.items():
        os.makedirs(path, exist_ok=True)
        print(f"📁 Created test directory: {path}")
    
    print("\n🧪 Testing different download configurations:\n")
    
    # Scenario 1: Default behavior (current directory)
    print("1️⃣ SCENARIO: Default (current directory)")
    print(f"   Command: download_video('{test_url}')")
    print(f"   Expected location: {os.getcwd()}/[video_title].mp4")
    print("   ⚠️  Note: Not actually downloading to avoid clutter\n")
    
    # Scenario 2: Specific directory with template
    print("2️⃣ SCENARIO: Downloads folder with template")
    template_path = f"{test_dirs['downloads']}/%(title)s.%(ext)s"
    print(f"   Command: download_video('{test_url}', output_path='{template_path}')")
    print(f"   Expected location: {test_dirs['downloads']}/[video_title].mp4")
    
    # Simulate this one
    print("   🔄 Simulating this download...")
    result = extractor.download_video(test_url, output_path=template_path)
    if result.get('success'):
        print("   ✅ Download successful!")
        downloaded_files = os.listdir(test_dirs['downloads'])
        for file in downloaded_files:
            file_path = os.path.join(test_dirs['downloads'], file)
            size = os.path.getsize(file_path)
            print(f"   📁 Downloaded: {file} ({size:,} bytes)")
    else:
        print(f"   ❌ Download failed: {result.get('error')}")
    print()
    
    # Scenario 3: Organized by uploader
    print("3️⃣ SCENARIO: Organized by uploader")
    organized_path = f"{test_dirs['organized']}/%(uploader)s/%(title)s.%(ext)s"
    print(f"   Command: download_video('{test_url}', output_path='{organized_path}')")
    print(f"   Expected: Creates uploader folder inside {test_dirs['organized']}/")
    
    # Simulate
    print("   🔄 Simulating organized download...")
    result = extractor.download_video(test_url, output_path=organized_path)
    if result.get('success'):
        print("   ✅ Download successful!")
        # Walk directory tree to show organization
        for root, dirs, files in os.walk(test_dirs['organized']):
            level = root.replace(test_dirs['organized'], '').count(os.sep)
            indent = ' ' * 4 * level
            print(f"   📁 {indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"   📄 {sub_indent}{file} ({size:,} bytes)")
    print()
    
    # Scenario 4: Fixed filename
    print("4️⃣ SCENARIO: Fixed filename")
    fixed_path = f"{test_dirs['user_downloads']}/my_facebook_reel.mp4"
    print(f"   Command: download_video('{test_url}', output_path='{fixed_path}')")
    print(f"   Expected: Exact file at {fixed_path}")
    
    # Simulate
    print("   🔄 Simulating fixed filename download...")
    result = extractor.download_video(test_url, output_path=fixed_path)
    if result.get('success'):
        print("   ✅ Download successful!")
        if os.path.exists(fixed_path):
            size = os.path.getsize(fixed_path)
            print(f"   📄 File: {fixed_path} ({size:,} bytes)")
    print()
    
    # Show summary
    print("📊 SUMMARY OF DOWNLOAD LOCATIONS:")
    print("=" * 40)
    
    all_test_dirs = [test_dirs['downloads'], test_dirs['organized'], test_dirs['user_downloads']]
    total_files = 0
    total_size = 0
    
    for test_dir in all_test_dirs:
        if os.path.exists(test_dir):
            print(f"\n📁 {test_dir}:")
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    rel_path = os.path.relpath(file_path, test_dir)
                    print(f"   📄 {rel_path} ({size:,} bytes)")
                    total_files += 1
                    total_size += size
    
    print(f"\n🎉 Total: {total_files} files, {total_size:,} bytes downloaded")
    
    # Cleanup option
    print(f"\n🧹 To cleanup test files, run:")
    for test_dir in all_test_dirs:
        if os.path.exists(test_dir):
            print(f"   rm -rf {test_dir}")

if __name__ == "__main__":
    test_download_scenarios()