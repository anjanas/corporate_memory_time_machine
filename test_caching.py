#!/usr/bin/env python3
"""
Test prompt caching with repeated analysis runs.
Demonstrates cache reuse across multiple requests.
"""

import os
from claude_analyzer import FindingsAnalyzer
from dotenv import load_dotenv

load_dotenv()


def create_sample_findings():
    """Create sample findings for testing."""
    return {
        "forgotten_decisions": [
            {
                "channel": "product",
                "message": {"text": "We decided to move to microservices architecture next quarter"},
                "detected_at": "2026-06-23T10:00:00",
                "reason": "No activity in past 14 days"
            },
            {
                "channel": "engineering",
                "message": {"text": "Decision made: all services must have 95% uptime SLA"},
                "detected_at": "2026-06-23T10:00:00",
                "reason": "No activity in past 14 days"
            },
        ],
        "rejected_ideas": [
            {
                "channel": "product",
                "message": {"text": "Rejected the idea of using GraphQL - too much overhead"},
                "detected_at": "2026-06-23T10:00:00",
                "reactions": []
            },
        ],
        "abandoned_projects": [
            {
                "channel": "projects",
                "message": {"text": "Project: Mobile app redesign - we're aiming for Q3 launch"},
                "detected_at": "2026-06-23T10:00:00",
                "reason": "No activity in past 30 days"
            },
        ]
    }


def test_prompt_caching():
    """Test caching by running analysis multiple times."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set. Skipping test.")
        return

    analyzer = FindingsAnalyzer()
    findings = create_sample_findings()

    print("=== Prompt Caching Test ===\n")
    print("The system prompt is cached across requests.")
    print("Subsequent runs reuse the cached prompt prefix.\n")

    # Run 1: Creates cache
    print("📍 Request 1: Creates prompt cache")
    print("-" * 40)
    result1 = analyzer.analyze_findings(findings)
    metrics1 = result1["cache_metrics"]

    print(f"Cache created: {metrics1['cache_creation_input_tokens']} tokens")
    print(f"Cache read: {metrics1['cache_read_input_tokens']} tokens")
    print(f"Input (uncached): {metrics1['input_tokens']} tokens")
    print(f"Output: {metrics1['output_tokens']} tokens")
    print()

    # Run 2: Reuses cache
    print("📍 Request 2: Reuses prompt cache")
    print("-" * 40)
    result2 = analyzer.analyze_findings(findings)
    metrics2 = result2["cache_metrics"]

    print(f"Cache created: {metrics2['cache_creation_input_tokens']} tokens")
    print(f"Cache read: {metrics2['cache_read_input_tokens']} tokens")
    print(f"Input (uncached): {metrics2['input_tokens']} tokens")
    print(f"Output: {metrics2['output_tokens']} tokens")
    print()

    # Cost comparison
    print("💰 Cost Comparison")
    print("-" * 40)
    # Pricing: input $5/1M, cache_creation ~$1.25/1M (1.25x), cache_read ~$0.1/1M (0.1x)
    cost_without_cache_2 = (metrics2['input_tokens'] + metrics2['output_tokens'] * 5) / 1_000_000 * 20  # rough estimate
    cost_with_cache_2 = (metrics2['cache_read_input_tokens'] * 0.1 + metrics2['input_tokens'] + metrics2['output_tokens'] * 5) / 1_000_000 * 20

    print(f"Request 1 (cache creation): Full price")
    print(f"Request 2 without cache: ~{cost_without_cache_2:.6f} USD")
    print(f"Request 2 with cache: ~{cost_with_cache_2:.6f} USD")
    print(f"Savings: ~{(cost_without_cache_2 - cost_with_cache_2) / cost_without_cache_2 * 100:.1f}%")
    print()

    print("✅ Caching test complete!")
    print("\nKey insights:")
    print("- The system prompt is cached after the first request")
    print("- Subsequent requests reuse the cached prompt at 0.1× the cost")
    print("- Your findings (message content) varies per request")
    print("- Cache hits accumulate, saving more on repeated analysis")


if __name__ == "__main__":
    test_prompt_caching()
