#!/usr/bin/env python3
"""
Test MCP protocol basics
"""

import asyncio
import json
import sys
sys.path.append('.')

from server import server

async def test_mcp_protocol():
    """Test basic MCP protocol functionality"""
    print("🔌 Testing MCP Protocol Basics")
    print("=" * 40)
    
    # Test list_tools
    print("1️⃣ Testing list_tools...")
    try:
        tools = await server.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test capabilities
    print("2️⃣ Testing server capabilities...")
    try:
        capabilities = server.get_capabilities()
        print(f"✅ Server capabilities: {capabilities}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    print("🎉 MCP protocol basics working!")

if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())