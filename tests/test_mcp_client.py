#!/usr/bin/env python3
"""Quick test for MCP client connectivity."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_client import SlackMCPClient


async def test_mcp_client():
    """Test MCP client methods."""
    print("Testing MCP Client Connection...\n")

    async with SlackMCPClient() as client:
        # Test 1: List conversations
        print("1. Fetching channels from Slack MCP server...")
        channels = await client.list_conversations(limit=5)
        print(f"   ✓ Found {len(channels)} channels")
        if channels:
            for ch in channels[:3]:
                print(f"     - #{ch.get('name')} (ID: {ch.get('id')})")

        # Test 2: Search messages
        print("\n2. Searching for 'decision' messages...")
        search_results = await client.search_messages("decision", count=10)
        print(f"   ✓ Found {len(search_results.get('matches', []))} matches")

        # Test 3: Get channel history
        if channels:
            channel_id = channels[0]["id"]
            channel_name = channels[0]["name"]
            print(f"\n3. Fetching history from #{channel_name}...")
            messages = await client.get_conversation_history(channel_id, limit=5)
            print(f"   ✓ Found {len(messages)} messages")

        print("\n✅ MCP Client tests completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
