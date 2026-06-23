"""Configuration for Slack Memory Agent."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Slack API
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")
    SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

    # MCP Server
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")

    # Analysis Settings
    DAYS_BACK = int(os.getenv("DAYS_BACK", "30"))
    MIN_DECISION_INACTIVITY_DAYS = int(os.getenv("MIN_DECISION_INACTIVITY_DAYS", "14"))
    MIN_PROJECT_INACTIVITY_DAYS = int(os.getenv("MIN_PROJECT_INACTIVITY_DAYS", "30"))

    # Keywords for detection
    DECISION_KEYWORDS = [
        "we decided",
        "we agreed",
        "decision made",
        "will proceed with",
        "approved",
        "consensus is",
    ]

    REJECTION_KEYWORDS = [
        "rejected",
        "nope",
        "won't do",
        "not doing",
        "decided against",
        "shot down",
        "no go",
        "vetoed",
    ]

    PROJECT_KEYWORDS = [
        "project:",
        "initiative:",
        "project discussion",
        "epic:",
        "roadmap item",
    ]

    # Output
    OUTPUT_FILE = "memory_analysis.json"
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
