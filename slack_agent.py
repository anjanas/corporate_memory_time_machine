#!/usr/bin/env python3
"""
Slack Memory Agent: Detects forgotten decisions, rejected ideas, and abandoned projects.
Uses MCP server to connect to Slack and Claude API for intelligent analysis.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from claude_analyzer import FindingsAnalyzer

load_dotenv()


class SlackMemoryAgent:
    def __init__(self, slack_token: Optional[str] = None, use_claude: bool = True):
        self.slack_token = slack_token or os.getenv("SLACK_TOKEN")
        self.workspace_cache = {}
        self.analysis_results = {
            "forgotten_decisions": [],
            "rejected_ideas": [],
            "abandoned_projects": []
        }
        self.use_claude = use_claude
        if use_claude:
            self.analyzer = FindingsAnalyzer()

    def analyze_workspace(self, days_back: int = 30) -> dict:
        """
        Analyze Slack workspace for forgotten decisions, rejected ideas, abandoned projects.

        Args:
            days_back: Number of days to look back (default 30)

        Returns:
            Dictionary with analysis results
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)

        channels = self.get_channels()

        for channel in channels:
            self.analyze_channel(channel, cutoff_date)

        return self.analysis_results

    def get_channels(self) -> list:
        """Fetch all channels from workspace via MCP."""
        # TODO: Implement MCP client call to list_conversations
        return []

    def analyze_channel(self, channel: dict, cutoff_date: datetime):
        """Analyze a single channel for signals."""
        messages = self.fetch_messages(channel["id"], cutoff_date)

        for message in messages:
            self.detect_forgotten_decision(message, channel)
            self.detect_rejected_idea(message, channel)
            self.detect_abandoned_thread(message, channel)

    def fetch_messages(self, channel_id: str, cutoff_date: datetime) -> list:
        """Fetch messages from a channel via MCP."""
        # TODO: Implement MCP client call to get_messages
        return []

    def detect_forgotten_decision(self, message: dict, channel: dict):
        """Identify messages about decisions that may have been forgotten."""
        decision_keywords = ["we decided", "we agreed", "decision made", "will proceed with"]
        text = message.get("text", "").lower()

        if any(kw in text for kw in decision_keywords):
            # Check if there's been no follow-up activity
            if self.has_no_followup(message, channel, days=14):
                self.analysis_results["forgotten_decisions"].append({
                    "channel": channel["name"],
                    "message": message,
                    "detected_at": datetime.now().isoformat(),
                    "reason": "No activity in past 14 days"
                })

    def detect_rejected_idea(self, message: dict, channel: dict):
        """Identify messages about rejected ideas."""
        rejection_keywords = ["rejected", "nope", "won't", "not doing", "decided against", "shot down"]
        text = message.get("text", "").lower()

        if any(kw in text for kw in rejection_keywords):
            # Check reactions and thread context
            reactions = message.get("reactions", [])
            self.analysis_results["rejected_ideas"].append({
                "channel": channel["name"],
                "message": message,
                "detected_at": datetime.now().isoformat(),
                "reactions": reactions
            })

    def detect_abandoned_thread(self, message: dict, channel: dict):
        """Identify project threads with no recent activity."""
        project_keywords = ["project:", "initiative:", "project discussion"]
        text = message.get("text", "").lower()

        if any(kw in text for kw in project_keywords):
            if self.has_no_followup(message, channel, days=30):
                self.analysis_results["abandoned_projects"].append({
                    "channel": channel["name"],
                    "message": message,
                    "detected_at": datetime.now().isoformat(),
                    "reason": "No activity in past 30 days"
                })

    def has_no_followup(self, message: dict, channel: dict, days: int = 14) -> bool:
        """Check if message has no recent replies or context."""
        # TODO: Implement logic to check thread activity
        return False

    def export_results(self, output_file: str = "memory_analysis.json"):
        """Export analysis results to file."""
        with open(output_file, "w") as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        print(f"Analysis saved to {output_file}")

    def analyze_with_claude(self) -> Optional[dict]:
        """
        Analyze findings with Claude using prompt caching.

        Returns the analysis with cache metrics, or None if Claude is disabled.
        """
        if not self.use_claude:
            return None

        print("\n[Claude Analysis with Prompt Caching]")
        analysis = self.analyzer.analyze_findings(self.analysis_results)

        # Print cache metrics
        metrics = analysis["cache_metrics"]
        print(f"Cache Read Tokens: {metrics['cache_read_input_tokens']}")
        print(f"Cache Creation Tokens: {metrics['cache_creation_input_tokens']}")
        print(f"Input Tokens (uncached): {metrics['input_tokens']}")
        print(f"Output Tokens: {metrics['output_tokens']}")

        return analysis

    def print_summary(self):
        """Print a summary of findings."""
        print("\n=== Slack Memory Analysis ===")
        print(f"Forgotten Decisions: {len(self.analysis_results['forgotten_decisions'])}")
        print(f"Rejected Ideas: {len(self.analysis_results['rejected_ideas'])}")
        print(f"Abandoned Projects: {len(self.analysis_results['abandoned_projects'])}")
        print("=" * 30)


if __name__ == "__main__":
    # Initialize agent with Claude analysis enabled
    agent = SlackMemoryAgent(use_claude=True)

    # Analyze workspace for forgotten decisions, rejected ideas, abandoned projects
    results = agent.analyze_workspace(days_back=30)
    agent.print_summary()

    # Analyze findings with Claude (uses prompt caching)
    claude_analysis = agent.analyze_with_claude()

    if claude_analysis:
        # Generate formatted report
        report = agent.analyzer.generate_report(agent.analysis_results)
        print("\n" + report)

        # Save report to file
        with open("findings_analysis.md", "w") as f:
            f.write(report)
        print("\n✓ Report saved to findings_analysis.md")

    # Export raw findings
    agent.export_results()
