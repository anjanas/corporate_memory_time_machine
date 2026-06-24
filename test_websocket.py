#!/usr/bin/env python3
"""
Test Socket Mode WebSocket connection to Slack.
"""

import os
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from dotenv import load_dotenv

load_dotenv()


def handle_events(client, req):
    """Handle incoming Socket Mode events."""
    print(f"\n📨 Received event: {req['type']}")
    if req["type"] == "hello":
        print("✅ Socket Mode connection established!")
    elif req["type"] == "slash_commands":
        print(f"🎯 Slash command: {req['payload'].get('command')}")
        response = SocketModeResponse(envelope_id=req["envelope_id"])
        client.send_socket_mode_response(response)
    else:
        response = SocketModeResponse(envelope_id=req["envelope_id"])
        client.send_socket_mode_response(response)


def test_connection():
    """Test the WebSocket connection."""
    app_token = os.getenv("SLACK_APP_TOKEN")

    if not app_token:
        print("❌ Error: SLACK_APP_TOKEN not found in .env")
        return False

    print("🔌 Testing Socket Mode WebSocket connection...")
    print(f"   App Token: {app_token[:20]}...")
    print()

    try:
        client = SocketModeClient(
            app_token=app_token,
            trace_enabled=False
        )

        # Add event listener
        client.socket_mode_request_listeners.append(handle_events)

        print("📡 Connecting to Slack Socket Mode...")
        client.connect()

        print("✅ WebSocket connected successfully!")
        print("\n📊 Connection Status:")
        print(f"   - Connected: {client.is_connected()}")
        print(f"   - App Token: {app_token[:30]}...")
        print("\n🎧 Listening for events...")
        print("   Type /memory-machine in your Slack workspace to test")
        print("   (Press Ctrl+C to stop)\n")

        # Keep running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\n⏹️  Closing connection...")
            client.close()
            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
