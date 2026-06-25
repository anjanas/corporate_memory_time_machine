# Slack Corporate Memory Time Machine

An agent that checks Slack for forgotten decisions, rejected ideas, and abandoned projects using MCP (Model Context Protocol) server integration.

## Overview

This tool analyzes your Slack workspace to surface:
- **Forgotten Decisions**: Important decisions made but never acted upon
- **Rejected Ideas**: Ideas that were explicitly rejected or shot down
- **Abandoned Projects**: Initiatives that lost momentum and were never completed

It then uses **Claude API with prompt caching** to intelligently analyze these findings, providing:
- Summarized insights about each finding
- Impact assessment and recommendations
- Priority ranking and suggested owners
- Formatted reports for sharing with teams

**Prompt Caching Benefit:** The analysis instructions are cached after the first analysis, so subsequent runs reuse the cached prompt at ~90% cost savings.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:
- `SLACK_TOKEN`: Bot token with workspace permissions (e.g., `xoxb-...`)
- `SLACK_SIGNING_SECRET`: For webhook verification
- `MCP_SERVER_URL`: URL where your Slack MCP server is running

### 3. Set Up Slack App

1. Go to https://api.slack.com/apps
2. Create a new app (or use existing)
3. Under "OAuth & Permissions", add these bot scopes:
   - `channels:read` - Read channel info
   - `chat:read` - Read messages
   - `users:read` - Read user profiles
   - `search:read` - Search messages (if using search)
4. Copy the Bot User OAuth Token to your `.env` as `SLACK_TOKEN`

### 4. Set Up Claude API (for intelligent analysis)

1. Go to https://console.anthropic.com/
2. Create an API key
3. Copy it to your `.env` as `ANTHROPIC_API_KEY`

The agent will use Claude to analyze findings with **prompt caching** — the system prompt caches after the first analysis and is reused on subsequent runs at ~90% cost savings.

### 4. Set Up MCP Server

The agent expects a Slack MCP server running (e.g., via Claude's official Slack MCP integration).

Configure the server connection in your `.env`:
```
MCP_SERVER_URL=http://localhost:3000
```

## Usage

### Basic Analysis

```bash
python slack_agent.py
```

This will:
1. Analyze the past 30 days of Slack messages
2. Detect forgotten decisions, rejected ideas, abandoned projects
3. Export results to `memory_analysis.json`
4. Print a summary to stdout

### Advanced Usage

```python
from slack_agent import SlackMemoryAgent

agent = SlackMemoryAgent()
results = agent.analyze_workspace(days_back=60)

# Access results
print(agent.analysis_results)

# Export to custom file
agent.export_results("my_analysis.json")
```

## Configuration

All settings can be customized in `.env`:

```bash
# How far back to analyze
DAYS_BACK=30

# Inactivity thresholds
MIN_DECISION_INACTIVITY_DAYS=14
MIN_PROJECT_INACTIVITY_DAYS=30

# Enable verbose output
VERBOSE=true
```

## Project Structure

```
.
├── slack_agent.py         # Main agent logic
├── mcp_client.py          # MCP server integration
├── claude_analyzer.py     # Claude API analysis with prompt caching
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── tests/                # Test scripts
│   └── test_caching.py   # Test script to verify prompt caching
└── README.md             # This file
```

## How Prompt Caching Works

**The Problem:** Analyzing Slack findings repeatedly costs money. The analysis instructions (system prompt) are expensive but identical across runs.

**The Solution:** Prompt caching caches the analysis instructions after the first request. Subsequent requests reuse the cached prefix at ~10% of the cost.

**In this project:**
- **Stable (cached)**: Analysis instructions in the system prompt
- **Volatile (uncached)**: Your Slack findings (changes each run)
- **Benefit**: After the first analysis, each subsequent run saves ~90% on prompt tokens

**Test it:**
```bash
python tests/test_caching.py
```

This script runs analysis twice and shows cache metrics. You'll see `cache_read_input_tokens` increase on the second run as the cached prompt is reused.

## How It Works

1. **Connects to MCP Server**: Establishes connection to Slack MCP server
2. **Lists Channels**: Fetches all accessible channels
3. **Analyzes Messages**: Looks for decision/rejection/project keywords
4. **Detects Patterns**:
   - Forgotten decisions: Messages with decision keywords + no recent activity
   - Rejected ideas: Messages with rejection keywords
   - Abandoned projects: Project mentions + inactivity > threshold
5. **Exports Results**: Saves findings to JSON with metadata

## TODO / Next Steps

- [x] Add Claude API integration for intelligent analysis
- [x] Implement prompt caching for cost efficiency
- [ ] Implement actual MCP client methods (currently stubbed)
- [ ] Add async/await for parallel channel analysis
- [ ] Implement thread reply fetching for context
- [ ] Add sentiment analysis for decision confidence
- [ ] Create CLI with more options (filter by channel, user, date range)
- [ ] Add persistence to track changes over time
- [ ] Implement deduplication for recurring signals
- [ ] Add Slack interactivity (buttons to revisit, archive, etc.)
- [ ] Build Slack app integration to post findings directly to channels

## Permissions Required

The Slack bot needs these permissions:
- `channels:read` - List and access channel info
- `chat:read` - Read channel messages
- `users:read` - Get user information
- `search:read` - (Optional) Search across workspace

## Output Format

`memory_analysis.json` structure:

```json
{
  "forgotten_decisions": [
    {
      "channel": "product",
      "message": {...},
      "detected_at": "2026-06-23T...",
      "reason": "No activity in past 14 days"
    }
  ],
  "rejected_ideas": [...],
  "abandoned_projects": [...]
}
```

## Contributing

Extend detection logic by:
1. Adding keywords to `config.py`
2. Implementing new detection methods in `SlackMemoryAgent`
3. Updating MCP client methods to fetch additional context

## License

MIT
