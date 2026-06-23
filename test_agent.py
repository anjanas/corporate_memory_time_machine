#!/usr/bin/env python3
"""
Example test file with mock data for developing the agent.
"""

import json
from datetime import datetime, timedelta
from slack_agent import SlackMemoryAgent


def create_mock_data():
    """Create sample Slack messages for testing."""
    now = datetime.now()

    return {
        "messages": [
            {
                "text": "We decided to move to microservices architecture next quarter",
                "ts": (now - timedelta(days=45)).timestamp(),
                "user": "alice",
                "reactions": ["decision"]
            },
            {
                "text": "Rejected the idea of using GraphQL - too much overhead",
                "ts": (now - timedelta(days=30)).timestamp(),
                "user": "bob",
                "reactions": []
            },
            {
                "text": "Project: Mobile app redesign - we're aiming for Q3 launch",
                "ts": (now - timedelta(days=60)).timestamp(),
                "user": "carol",
                "reactions": []
            },
            {
                "text": "We agreed on using Python for the data pipeline",
                "ts": (now - timedelta(days=20)).timestamp(),
                "user": "dave",
                "reactions": []
            },
            {
                "text": "Decision made: all services must have 95% uptime SLA",
                "ts": (now - timedelta(days=50)).timestamp(),
                "user": "eve",
                "reactions": []
            },
            {
                "text": "Initiative: Cost optimization - nope, not in budget this year",
                "ts": (now - timedelta(days=35)).timestamp(),
                "user": "frank",
                "reactions": []
            },
        ]
    }


def test_detection_logic():
    """Test the detection logic with mock data."""
    agent = SlackMemoryAgent()

    mock_data = create_mock_data()
    mock_channel = {"id": "C123", "name": "engineering"}

    print("Testing detection logic with mock data...\n")

    for message in mock_data["messages"]:
        print(f"Message: {message['text'][:60]}...")
        print(f"  Timestamp: {datetime.fromtimestamp(message['ts'])}")

        agent.detect_forgotten_decision(message, mock_channel)
        agent.detect_rejected_idea(message, mock_channel)
        agent.detect_abandoned_thread(message, mock_channel)

    agent.print_summary()

    print("\n=== Forgotten Decisions ===")
    for item in agent.analysis_results["forgotten_decisions"]:
        print(f"  - {item['message']['text'][:60]}")

    print("\n=== Rejected Ideas ===")
    for item in agent.analysis_results["rejected_ideas"]:
        print(f"  - {item['message']['text'][:60]}")

    print("\n=== Abandoned Projects ===")
    for item in agent.analysis_results["abandoned_projects"]:
        print(f"  - {item['message']['text'][:60]}")


def test_export():
    """Test exporting results."""
    agent = SlackMemoryAgent()

    # Add sample data
    agent.analysis_results["forgotten_decisions"] = [
        {
            "channel": "engineering",
            "message": {"text": "We decided to move to microservices"},
            "detected_at": datetime.now().isoformat(),
            "reason": "No activity in past 14 days"
        }
    ]

    agent.export_results("test_output.json")
    print("✓ Export test successful")

    # Clean up
    import os
    if os.path.exists("test_output.json"):
        os.remove("test_output.json")


if __name__ == "__main__":
    print("=== Slack Memory Agent Tests ===\n")
    test_detection_logic()
    print("\n" + "=" * 40 + "\n")
    test_export()
