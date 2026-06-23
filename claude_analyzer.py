"""
Claude-powered analysis of Slack memory findings with prompt caching.
Uses cached system prompts to efficiently analyze repeated findings patterns.
"""

import json
import os
from typing import Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class FindingsAnalyzer:
    """Analyzes Slack memory findings using Claude with prompt caching."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-7"

        # Cached system prompt for analyzing findings
        self.system_prompt = """You are an expert organizational analyst specializing in team dynamics and project management.

Your task is to analyze forgotten decisions, rejected ideas, and abandoned projects from Slack communications.
For each finding, provide:

1. **Summary**: A concise description of what was found
2. **Impact**: What the consequence of this forgotten/rejected/abandoned item is
3. **Recommendation**: A specific action to address it (revisit decision, revive idea, restart project, etc.)
4. **Priority**: Mark as High, Medium, or Low based on potential impact
5. **Owner**: Who should own addressing this (if discernible from context)

Be actionable and pragmatic. Focus on items that represent missed opportunities or organizational risks."""

    def analyze_findings(self, findings: dict, include_details: bool = True) -> dict:
        """
        Analyze collected findings with Claude using prompt caching.

        The system prompt is cached across requests, so repeated analysis
        of new findings reuses the expensive prompt prefix.

        Args:
            findings: Dict with 'forgotten_decisions', 'rejected_ideas', 'abandoned_projects'
            include_details: Whether to include raw finding details in response

        Returns:
            Dict with analysis results and cache usage metrics
        """
        # Prepare findings summary
        findings_text = self._format_findings(findings)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"}  # Cache the analysis instructions
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Please analyze these Slack memory findings:

{findings_text}

Provide detailed analysis for each category. Prioritize actionable insights."""
                }
            ]
        )

        # Extract analysis text
        analysis_text = next(
            (block.text for block in response.content if block.type == "text"),
            ""
        )

        # Return results with cache metrics
        return {
            "analysis": analysis_text,
            "cache_metrics": {
                "cache_creation_input_tokens": response.usage.cache_creation_input_tokens,
                "cache_read_input_tokens": response.usage.cache_read_input_tokens,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "findings_summary": {
                "forgotten_decisions_count": len(findings.get("forgotten_decisions", [])),
                "rejected_ideas_count": len(findings.get("rejected_ideas", [])),
                "abandoned_projects_count": len(findings.get("abandoned_projects", [])),
            }
        }

    def generate_report(self, findings: dict, title: str = "Slack Corporate Memory Analysis") -> str:
        """Generate a formatted report from findings and analysis."""
        analysis = self.analyze_findings(findings)

        report = f"""# {title}

## Executive Summary
- **Forgotten Decisions**: {analysis['findings_summary']['forgotten_decisions_count']}
- **Rejected Ideas**: {analysis['findings_summary']['rejected_ideas_count']}
- **Abandoned Projects**: {analysis['findings_summary']['abandoned_projects_count']}

## Cache Efficiency
- **Cached tokens reused**: {analysis['cache_metrics']['cache_read_input_tokens']}
- **Tokens cached this request**: {analysis['cache_metrics']['cache_creation_input_tokens']}
- **New tokens processed**: {analysis['cache_metrics']['input_tokens']}
- **Output tokens**: {analysis['cache_metrics']['output_tokens']}

## Analysis

{analysis['analysis']}

---
*Report generated with Claude Opus 4.7 using prompt caching for efficiency*
"""
        return report

    def _format_findings(self, findings: dict) -> str:
        """Format findings dict into readable text."""
        sections = []

        # Forgotten decisions
        if findings.get("forgotten_decisions"):
            sections.append("## Forgotten Decisions")
            for item in findings["forgotten_decisions"]:
                msg = item["message"]
                sections.append(f"- {msg.get('text', 'N/A')[:100]}... (in #{item['channel']})")

        # Rejected ideas
        if findings.get("rejected_ideas"):
            sections.append("\n## Rejected Ideas")
            for item in findings["rejected_ideas"]:
                msg = item["message"]
                sections.append(f"- {msg.get('text', 'N/A')[:100]}... (in #{item['channel']})")

        # Abandoned projects
        if findings.get("abandoned_projects"):
            sections.append("\n## Abandoned Projects")
            for item in findings["abandoned_projects"]:
                msg = item["message"]
                sections.append(f"- {msg.get('text', 'N/A')[:100]}... (in #{item['channel']})")

        return "\n".join(sections) if sections else "No findings to analyze."
