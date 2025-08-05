#!/usr/bin/env python3
"""
Test MCP tools with security enhancements
"""

import sys
import json
import asyncio
import tempfile
import os

sys.path.append('.')
from server import handle_call_tool

async def test_get_download_locations():
    """Test get_download_locations tool"""
    print("📁 Testing get_download_locations tool")
    print("=" * 45)
    
    try:
        result = await handle_call_tool("get_download_locations", {})
        response = json.loads(result[0].text)
        
        if response.get("success"):
            print("✅ Tool call successful")
            locations = response["locations"]
            print(f"   Found {len(locations)} locations:")
            for location_id, info in locations.items():
                print(f"   - {location_id}: {info['original']} ({'✓' if info['writable'] else '✗'})")
        else:
            print(f"❌ Tool call failed: {response.get('error')}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    print()

async def test_secure_download():
    """Test secure download_video tool"""
    print("🔒 Testing secure download_video tool")
    print("=" * 45)
    
    test_url = "https://www.facebook.com/reel/721818657509109"
    
    # Test new secure interface
    print("🧪 Testing secure location-based download:")
    try:
        result = await handle_call_tool("download_video", {
            "url": test_url,
            "location_id": "default",
            "relative_path": "test_security",
            "filename_template": "%(title)s.%(ext)s"
        })
        
        response = json.loads(result[0].text)
        if response.get("success"):
            print("✅ Secure download successful")
            print(f"   Downloaded to: {response.get('download_path')}")
            
            # Check if file actually exists
            download_path = response.get('download_path')
            if download_path and os.path.exists(download_path):
                size = os.path.getsize(download_path)
                print(f"   File size: {size:,} bytes")
            else:
                print("   ⚠️  File path returned but file not found (may be template)")
        else:
            print(f"❌ Secure download failed: {response.get('error')}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    print()
    
    # Test security validation
    print("🛡️  Testing security validation:")
    security_tests = [
        {
            "name": "Invalid location",
            "args": {
                "url": test_url,
                "location_id": "nonexistent"
            }
        },
        {
            "name": "Path traversal attempt",
            "args": {
                "url": test_url,
                "location_id": "default",
                "relative_path": "../../../etc/passwd"
            }
        },
        {
            "name": "Legacy output_path (deprecated)",
            "args": {
                "url": test_url,
                "output_path": "/tmp/legacy_test.mp4"
            }
        }
    ]
    
    for test in security_tests:
        print(f"   Testing: {test['name']}")
        try:
            result = await handle_call_tool("download_video", test["args"])
            response = json.loads(result[0].text)
            
            if response.get("success"):
                print(f"   ✅ Allowed: {response.get('download_path', 'No path')}")
            else:
                print(f"   🛡️  Blocked: {response.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

async def main():
    """Run all security tests"""
    print("🔐 Testing MCP Security Enhancements")
    print("=" * 50)
    print()
    
    await test_get_download_locations()
    await test_secure_download()
    
    print("🎉 MCP security testing completed!")

if __name__ == "__main__":
    asyncio.run(main())