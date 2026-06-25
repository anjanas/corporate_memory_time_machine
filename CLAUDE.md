# Slack Corporate Memory Time Machine

## Overview

Agent that analyzes Slack workspace to surface forgotten decisions, rejected ideas, and abandoned projects using MCP server integration.

## Architecture

### Core Components

1. **SlackMemoryAgent** (`slack_agent.py`)
   - Main analysis engine
   - Detects three signal types: forgotten decisions, rejected ideas, abandoned projects
   - Exports results as JSON

2. **SlackMCPClient** (`mcp_client.py`)
   - Handles communication with Slack MCP server
   - Wraps MCP resource calls (conversations.list, conversations.history, search.messages)
   - Async/await for parallel operations

3. **Config** (`config.py`)
   - Centralized keyword definitions and settings
   - Environment variable management

## Detection Strategy

### Forgotten Decisions
- **Signal**: Messages containing decision keywords + inactivity
- **Keywords**: "we decided", "we agreed", "decision made", "approved"
- **Threshold**: No activity in past 14 days (configurable)

### Rejected Ideas
- **Signal**: Messages containing rejection keywords
- **Keywords**: "rejected", "nope", "won't", "decided against", "vetoed"
- **Context**: Reactions, thread replies

### Abandoned Projects
- **Signal**: Project keywords + long inactivity
- **Keywords**: "project:", "initiative:", "epic:"
- **Threshold**: No activity in past 30 days (configurable)

## Implementation TODOs

1. **MCP Client Methods** - Currently stubbed in `mcp_client.py`:
   - `list_conversations()` - Fetch channels
   - `get_conversation_history()` - Get messages
   - `get_thread_replies()` - Get thread context
   - `search_messages()` - Search by keyword

2. **Activity Detection** - Implement in `has_no_followup()`:
   - Check thread reply count
   - Check reaction count
   - Check timestamp gap to next message
   - Define "recent activity" threshold

3. **Async Operations** - Make channel analysis parallel:
   - Use asyncio to fetch multiple channels concurrently
   - Thread the MCP client through analyze_channel

4. **Deduplication** - Track seen findings:
   - Same decision mentioned multiple times
   - Related rejected ideas
   - Track across runs

5. **CLI Interface** - Add argument parsing:
   - Filter by channel/user/date range
   - Custom output format
   - Interactive mode to revisit items

6. **Persistence** - Store state between runs:
   - Track previously found items
   - Highlight new findings
   - Generate diffs/reports

## Testing

Run mock tests with `python tests/test_agent.py` to verify detection logic without MCP server.

## Environment Setup

```bash
cp .env.example .env
# Fill in SLACK_TOKEN and MCP_SERVER_URL
pip install -r requirements.txt
python slack_agent.py
```

## Key Design Decisions

- **Keyword-based detection**: Simple, fast, extensible. Trade-off: misses implicit signals.
- **JSON output**: Enables easy downstream processing and integration.
- **Configurable thresholds**: Different activity timelines per signal type.
- **Async-ready architecture**: MCP client supports concurrent operations.
