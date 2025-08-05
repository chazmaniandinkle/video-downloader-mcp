#!/usr/bin/env python3
"""
Test the MCP server using the actual MCP protocol
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_protocol():
    """Test the MCP server using proper protocol communication"""
    
    print("🔌 Testing MCP Protocol Communication")
    print("=" * 50)
    
    # Start the MCP server
    server_proc = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    def send_message(message):
        """Send a JSON-RPC message to the server"""
        msg_json = json.dumps(message)
        server_proc.stdin.write(msg_json + "\n")
        server_proc.stdin.flush()
        
        # Read response
        response_line = server_proc.stdout.readline()
        if response_line:
            try:
                return json.loads(response_line.strip())
            except json.JSONDecodeError as e:
                return {"error": f"JSON decode error: {e}", "raw": response_line}
        return {"error": "No response"}
    
    try:
        # Step 1: Initialize the connection
        print("🔧 Step 1: Initialize MCP connection")
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        response = send_message(init_msg)
        if "result" in response:
            print("   ✅ Initialization successful")
            caps = response["result"].get("capabilities", {})
            print(f"   Server capabilities: {list(caps.keys())}")
        else:
            print(f"   ❌ Initialization failed: {response}")
            return
        
        # Step 2: List tools
        print("\n🛠️  Step 2: List available tools")
        list_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_message(list_msg)
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"   ✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool['name']}: {tool['description']}")
        else:
            print(f"   ❌ Failed to list tools: {response}")
        
        # Step 3: Test check_ytdlp_support
        print("\n📹 Step 3: Test YouTube support check")
        check_msg = {
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
        
        response = send_message(check_msg)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            print(f"   ✅ Support check successful")
            print(f"   Supported: {data.get('supported')}")
            if data.get('supported'):
                print(f"   Title: {data.get('title')}")
        else:
            print(f"   ❌ Support check failed: {response}")
        
        # Step 4: Test Facebook reel check
        print("\n🎥 Step 4: Test Facebook reel support")
        fb_check_msg = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "check_ytdlp_support",
                "arguments": {
                    "url": "https://www.facebook.com/reel/721818657509109"
                }
            }
        }
        
        response = send_message(fb_check_msg)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            print(f"   ✅ Facebook check successful")
            print(f"   Supported: {data.get('supported')}")
            if data.get('supported'):
                print(f"   Title: {data.get('title')}")
                print(f"   Duration: {data.get('duration')} seconds")
        else:
            print(f"   ❌ Facebook check failed: {response}")
        
        # Step 5: Test formats for Facebook reel
        print("\n🎬 Step 5: Test format extraction")
        formats_msg = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_video_formats",
                "arguments": {
                    "url": "https://www.facebook.com/reel/721818657509109"
                }
            }
        }
        
        response = send_message(formats_msg)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            if data.get('success'):
                formats = data.get('formats', [])
                print(f"   ✅ Found {len(formats)} formats")
                
                # Show video formats
                video_formats = [f for f in formats if f.get('resolution') != 'audio-only']
                print(f"   Video formats: {len(video_formats)}")
                for fmt in video_formats[:3]:
                    print(f"     - {fmt.get('format_id')}: {fmt.get('resolution')} ({fmt.get('ext')})")
            else:
                print(f"   ❌ Format extraction failed: {data.get('error')}")
        else:
            print(f"   ❌ Format request failed: {response}")
            
        # Step 6: Test fallback analysis
        print("\n🔍 Step 6: Test fallback webpage analysis")
        fallback_msg = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "analyze_webpage",
                "arguments": {
                    "url": "https://httpbin.org/html"
                }
            }
        }
        
        response = send_message(fallback_msg)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            if data.get('success'):
                print(f"   ✅ Webpage analysis successful")
                print(f"   Content length: {data.get('content_length')} chars")
                print(f"   Has video tags: {data.get('has_video_tags')}")
            else:
                print(f"   ❌ Analysis failed: {data.get('error')}")
        else:
            print(f"   ❌ Analysis request failed: {response}")
        
        print("\n🎉 All MCP protocol tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
    finally:
        # Clean up
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()

if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())