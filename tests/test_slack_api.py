#!/usr/bin/env python3
"""Test script to fetch Slack messages using the token."""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# Initialize Slack client
token = os.getenv("SLACK_TOKEN")
if not token:
    print("Error: SLACK_TOKEN not found in .env")
    exit(1)

client = WebClient(token=token)

try:
    # List all conversations
    print("Fetching conversations list...")
    result = client.conversations_list(exclude_archived=True)

    channels = result["channels"]
    print(f"\n✓ Found {len(channels)} channels:\n")

    for channel in channels[:10]:  # Show first 10
        print(f"  • #{channel['name']} (ID: {channel['id']})")
        print(f"    Created: {channel.get('created', 'N/A')}")
        print(f"    Topic: {channel.get('topic', {}).get('value', 'N/A')}")
        print()

    # Get messages from first channel
    if channels:
        channel_id = channels[0]["id"]
        channel_name = channels[0]["name"]

        print(f"\nFetching messages from #{channel_name}...")
        history = client.conversations_history(channel=channel_id, limit=10)

        messages = history.get("messages", [])
        print(f"✓ Found {len(messages)} recent messages:\n")

        for msg in messages[:5]:  # Show first 5
            user = msg.get("user", "bot")
            text = msg.get("text", "[no text]")[:100]
            print(f"  • User {user}: {text}")
            print()

except SlackApiError as e:
    print(f"✗ Slack API Error: {e.response['error']}")
    print(f"  Details: {e.response}")
except Exception as e:
    print(f"✗ Error: {e}")
