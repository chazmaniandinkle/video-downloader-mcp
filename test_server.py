#!/usr/bin/env python3
"""
Test script for the Video Downloader MCP Server
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

async def test_mcp_server():
    """Test the MCP server by sending various requests"""
    
    print("🧪 Testing Video Downloader MCP Server")
    print("=" * 50)
    
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    def send_request(request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response"""
        request_json = json.dumps(request) + "\n"
        server_process.stdin.write(request_json)
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if not response_line:
            return {"error": "No response from server"}
        
        try:
            return json.loads(response_line.strip())
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {e}", "raw": response_line}
    
    try:
        # Test 1: Initialize the server
        print("🔧 Test 1: Server Initialization")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = send_request(init_request)
        print(f"   Response: {response}")
        
        # Test 2: List available tools
        print("\n🛠️  Test 2: List Tools")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = send_request(list_tools_request)
        print(f"   Found {len(response.get('result', {}).get('tools', []))} tools")
        for tool in response.get('result', {}).get('tools', []):
            print(f"   - {tool.get('name')}: {tool.get('description')}")
        
        # Test 3: Check yt-dlp support for YouTube
        print("\n📹 Test 3: Check YouTube Support")
        youtube_test_request = {
            "jsonrpc": "2.0", 
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "check_ytdlp_support",
                "arguments": {
                    "url": "https://www.youtube.com/watch?v=0HAql2TX9aw"
                }
            }
        }
        
        response = send_request(youtube_test_request)
        print(f"   Response: {response}")
        
        # Test 4: Get video formats
        print("\n🎥 Test 4: Get Video Formats")
        formats_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_video_formats", 
                "arguments": {
                    "url": "https://www.youtube.com/watch?v=0HAql2TX9aw"
                }
            }
        }
        
        response = send_request(formats_request)
        if response.get('result'):
            content = json.loads(response['result']['content'][0]['text'])
            if content.get('success'):
                print(f"   Found {len(content['formats'])} formats")
                print("   Sample formats:")
                for fmt in content['formats'][:3]:  # Show first 3
                    print(f"     - {fmt.get('format_id')}: {fmt.get('resolution')} ({fmt.get('ext')})")
            else:
                print(f"   Error: {content.get('error')}")
        
        # Test 5: Test fallback with unsupported URL
        print("\n🔍 Test 5: Fallback Analysis")
        fallback_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "analyze_webpage",
                "arguments": {
                    "url": "https://example.com"
                }
            }
        }
        
        response = send_request(fallback_request)
        print(f"   Response: {response}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        
        print("\n✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())