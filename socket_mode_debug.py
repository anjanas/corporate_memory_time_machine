#!/usr/bin/env python3
"""
Debug version of Socket Mode handler with detailed logging.
"""

import os
import time
import sys
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient
from dotenv import load_dotenv

load_dotenv()

def handle_events(client, req):
    """Handle all incoming Socket Mode events."""
    event_type = req.get("type", "unknown")
    print(f"\n📨 Event received: {event_type}", flush=True)
    print(f"   Payload keys: {list(req.keys())}", flush=True)

    if event_type == "hello":
        print("   ✅ Hello event - connection established", flush=True)
        response = SocketModeResponse(envelope_id=req["envelope_id"])
        client.send_socket_mode_response(response)

    elif event_type == "slash_commands":
        payload = req.get("payload", {})
        command = payload.get("command", "unknown")
        user = payload.get("user_id", "unknown")
        channel = payload.get("channel_id", "unknown")

        print(f"   🎯 Slash Command: {command}", flush=True)
        print(f"      User: {user}", flush=True)
        print(f"      Channel: {channel}", flush=True)

        # Acknowledge immediately
        response = SocketModeResponse(envelope_id=req["envelope_id"])
        client.send_socket_mode_response(response)
        print(f"   ✅ Acknowledged command", flush=True)

    else:
        print(f"   ℹ️  Other event type", flush=True)
        response = SocketModeResponse(envelope_id=req["envelope_id"])
        client.send_socket_mode_response(response)


def main():
    """Start the debug Socket Mode client."""
    app_token = os.getenv("SLACK_APP_TOKEN")

    if not app_token:
        print("❌ SLACK_APP_TOKEN not found in .env", flush=True)
        return

    print("🔌 Socket Mode Debug Handler", flush=True)
    print(f"   App Token: {app_token[:30]}...", flush=True)
    print("   Connecting...", flush=True)
    print(flush=True)

    try:
        client = SocketModeClient(app_token=app_token, trace_enabled=False)

        # Add event listener
        client.socket_mode_request_listeners.append(handle_events)

        print("📡 Connecting to Socket Mode...", flush=True)
        client.connect()

        print("✅ Connected! Waiting for events...", flush=True)
        print("   Try /memory-machine in Slack now", flush=True)
        print(flush=True)

        # Keep running
        while client.is_connected():
            time.sleep(1)

    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        print("Shutting down...", flush=True)


if __name__ == "__main__":
    main()
