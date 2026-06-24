#!/usr/bin/env python3
"""
Socket Mode handler for Memory Machine agent.
Listens for slash commands and invokes the agent.
"""

import asyncio
import os
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient
from dotenv import load_dotenv
from slack_agent import SlackMemoryAgent

load_dotenv()


def handle_events(client, req):
    """Handle incoming Socket Mode events."""
    if req["type"] == "slash_commands":
        command = req["payload"]
        print(f"\n🔍 Slash command received: {command.get('command')}")
        print(f"   User: {command.get('user_id')}, Channel: {command.get('channel_id')}")

        # Acknowledge the command
        response = SocketModeResponse(envelope_id=req["envelope_id"])
        client.send_socket_mode_response(response)

        # Run the agent
        try:
            asyncio.run(process_command(command, client))
        except Exception as e:
            print(f"❌ Error: {e}")


async def process_command(command, client):
    """Process the slash command and run the agent."""
    channel_id = command.get("channel_id")
    slack_token = os.getenv("SLACK_TOKEN")
    web_client = WebClient(token=slack_token)

    # Send initial response
    web_client.chat_postMessage(
        channel=channel_id,
        text="🤖 Memory Machine is analyzing your Slack workspace..."
    )

    # Run the agent
    agent = SlackMemoryAgent(use_claude=True)
    results = await agent.analyze_workspace(days_back=30)

    # Prepare summary
    forgotten = len(results["forgotten_decisions"])
    rejected = len(results["rejected_ideas"])
    abandoned = len(results["abandoned_projects"])

    summary = f"""
📊 *Memory Machine Analysis Complete*

✨ *Findings:*
• Forgotten Decisions: {forgotten}
• Rejected Ideas: {rejected}
• Abandoned Projects: {abandoned}

📄 Full report saved to files and Claude analysis generated.
    """

    # Send results
    web_client.chat_postMessage(
        channel=channel_id,
        text=summary.strip()
    )

    print(f"✅ Analysis complete: {forgotten} decisions, {rejected} ideas, {abandoned} projects")


def start_handler():
    """Start the Socket Mode client."""
    app_token = os.getenv("SLACK_APP_TOKEN")

    if not app_token:
        raise ValueError("SLACK_APP_TOKEN not found in .env")

    print("🚀 Memory Machine Socket Mode handler starting...")
    print(f"   App Token: {app_token[:20]}...")
    print("   Listening for /memory-machine command...\n")

    client = SocketModeClient(
        app_token=app_token,
        trace_enabled=False
    )

    client.socket_mode_request_listeners.append(handle_events)

    client.connect()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
        client.close()


if __name__ == "__main__":
    start_handler()
