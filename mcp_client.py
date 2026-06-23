"""
MCP Client for Slack Integration.
Handles communication with Slack MCP server.
"""

import asyncio
import json
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import httpx

load_dotenv()


class SlackMCPClient:
    def __init__(self):
        server_url = os.getenv("MCP_SERVER_URL")
        self.server_url = f"https://{server_url}" if server_url and not server_url.startswith("http") else server_url
        self.token = os.getenv("SLACK_TOKEN")
        self.session = None

    async def connect(self):
        """Initialize connection to MCP server."""
        self.session = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.token}"}
        )

    async def list_conversations(self, exclude_archived: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch list of conversations/channels.

        Args:
            exclude_archived: Whether to exclude archived channels
            limit: Maximum number of channels to fetch

        Returns:
            List of channel objects with id, name, created, topic, purpose
        """
        if not self.session:
            return []

        try:
            url = f"{self.server_url}/resources/slack:///conversations"
            response = await self.session.get(url)
            response.raise_for_status()
            data = response.json()

            channels = json.loads(data.get("contents", [{}])[0].get("text", "[]"))
            if exclude_archived:
                channels = [ch for ch in channels if not ch.get("is_archived", False)]
            return channels[:limit]
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return []

    async def get_conversation_history(
        self,
        channel_id: str,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch message history for a channel.

        Args:
            channel_id: Channel ID
            oldest: Timestamp to start from (unix epoch)
            latest: Timestamp to end at (unix epoch)
            limit: Max messages to fetch

        Returns:
            List of message objects
        """
        if not self.session:
            return []

        try:
            url = f"{self.server_url}/resources/slack:///conversations/{channel_id}/history"
            response = await self.session.get(url)
            response.raise_for_status()
            data = response.json()

            messages = json.loads(data.get("contents", [{}])[0].get("text", "[]"))
            return messages[:limit]
        except Exception as e:
            print(f"Error fetching conversation history: {e}")
            return []

    async def get_thread_replies(
        self,
        channel_id: str,
        thread_ts: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch replies in a thread.

        Args:
            channel_id: Channel ID
            thread_ts: Thread timestamp
            limit: Max replies to fetch

        Returns:
            List of reply messages
        """
        if not self.session:
            return []

        try:
            url = f"{self.server_url}/resources/slack:///conversations/{channel_id}/threads/{thread_ts}"
            response = await self.session.get(url)
            response.raise_for_status()
            data = response.json()

            messages = json.loads(data.get("contents", [{}])[0].get("text", "[]"))
            return messages[:limit]
        except Exception as e:
            print(f"Error fetching thread replies: {e}")
            return []

    async def search_messages(
        self,
        query: str,
        sort: str = "timestamp",
        count: int = 100
    ) -> Dict[str, Any]:
        """
        Search messages across workspace.

        Args:
            query: Search query (e.g., "decided on", "rejected")
            sort: Sort field (timestamp, score)
            count: Max results

        Returns:
            Search results with matches
        """
        if not self.session:
            return {"matches": []}

        try:
            url = f"{self.server_url}/tools/search_messages"
            payload = {"query": query, "count": count}
            response = await self.session.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            result = json.loads(data.get("content", [{}])[0].get("text", "{}"))
            return result
        except Exception as e:
            print(f"Error searching messages: {e}")
            return {"matches": []}

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        if not self.session:
            return {}

        try:
            url = f"{self.server_url}/tools/get_user_info"
            payload = {"user_id": user_id}
            response = await self.session.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            user_info = json.loads(data.get("content", [{}])[0].get("text", "{}"))
            return user_info
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return {}

    async def disconnect(self):
        """Clean up connection."""
        if self.session:
            await self.session.aclose()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


async def example_usage():
    """Example of using the MCP client."""
    async with SlackMCPClient() as client:
        # List all channels
        channels = await client.list_conversations()
        print(f"Found {len(channels)} channels")

        # Search for decisions
        results = await client.search_messages("we decided")
        print(f"Found {len(results.get('matches', []))} decisions")

        # Get history of a channel
        if channels:
            channel = channels[0]
            history = await client.get_conversation_history(channel["id"], limit=50)
            print(f"Got {len(history)} messages from {channel['name']}")


if __name__ == "__main__":
    asyncio.run(example_usage())
