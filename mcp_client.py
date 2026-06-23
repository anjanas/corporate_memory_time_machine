"""
MCP Client for Slack Integration.
Uses Slack SDK as MCP implementation for accessing Slack resources.
"""

import asyncio
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()


class SlackMCPClient:
    def __init__(self):
        self.token = os.getenv("SLACK_TOKEN")
        self.client = WebClient(token=self.token) if self.token else None

    async def connect(self):
        """Initialize connection to Slack."""
        if self.client:
            try:
                await asyncio.to_thread(self.client.auth_test)
                print("✓ Connected to Slack")
            except SlackApiError as e:
                raise RuntimeError(f"Could not authenticate: {e.response['error']}")

    async def list_conversations(self, exclude_archived: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch list of conversations/channels.

        Args:
            exclude_archived: Whether to exclude archived channels
            limit: Maximum number of channels to fetch

        Returns:
            List of channel objects with id, name, created, topic, purpose
        """
        if not self.client:
            return []

        try:
            result = await asyncio.to_thread(
                self.client.conversations_list,
                exclude_archived=exclude_archived,
                limit=limit
            )
            return result.get("channels", [])
        except SlackApiError as e:
            print(f"Error fetching conversations: {e.response['error']}")
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
        if not self.client:
            return []

        try:
            kwargs = {"channel": channel_id, "limit": limit}
            if oldest:
                kwargs["oldest"] = oldest
            if latest:
                kwargs["latest"] = latest

            result = await asyncio.to_thread(
                self.client.conversations_history,
                **kwargs
            )
            return result.get("messages", [])
        except SlackApiError as e:
            print(f"Error fetching conversation history: {e.response['error']}")
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
        if not self.client:
            return []

        try:
            result = await asyncio.to_thread(
                self.client.conversations_replies,
                channel=channel_id,
                ts=thread_ts,
                limit=limit
            )
            return result.get("messages", [])
        except SlackApiError as e:
            print(f"Error fetching thread replies: {e.response['error']}")
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
        if not self.client:
            return {"matches": []}

        try:
            result = await asyncio.to_thread(
                self.client.search_messages,
                query=query,
                sort_dir="desc",
                count=count
            )
            return {
                "matches": result.get("messages", []),
                "total": result.get("total", 0)
            }
        except SlackApiError as e:
            print(f"Error searching messages: {e.response['error']}")
            return {"matches": []}

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        if not self.client:
            return {}

        try:
            result = await asyncio.to_thread(
                self.client.users_info,
                user=user_id
            )
            return result.get("user", {})
        except SlackApiError as e:
            print(f"Error fetching user info: {e.response['error']}")
            return {}

    async def disconnect(self):
        """Clean up connection."""
        pass

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
