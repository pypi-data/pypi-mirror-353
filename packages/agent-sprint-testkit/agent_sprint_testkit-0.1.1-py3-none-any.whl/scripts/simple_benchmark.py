#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASTK Intelligent Benchmark Runner
=================================

A comprehensive benchmark tool for testing AI agents with diverse scenarios.

Usage:
    python scripts/simple_benchmark.py <agent_path>
    ./scripts/simple_benchmark.py <agent_path>

Example:
    python scripts/simple_benchmark.py examples/agents/file_qa_agent.py
"""

import asyncio
import json
import time
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


async def run_agent_scenario(agent_path: Path, scenario_name: str, query: str) -> dict:
    """Run agent with a specific scenario query"""
    print(f"Running scenario: {scenario_name}")

    start_time = time.time()

    try:
        # Run the agent with a specific test query
        result = subprocess.run([
            sys.executable, str(agent_path), query
        ], capture_output=True, text=True, timeout=45)

        end_time = time.time()
        duration = end_time - start_time

        return {
            "scenario": scenario_name,
            "query": query,
            "duration_seconds": duration,
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }

    except subprocess.TimeoutExpired:
        return {
            "scenario": scenario_name,
            "query": query,
            "duration_seconds": 45.0,
            "success": False,
            "output": "",
            "error": "Timeout after 45 seconds"
        }
    except Exception as e:
        return {
            "scenario": scenario_name,
            "query": query,
            "duration_seconds": 0.0,
            "success": False,
            "output": "",
            "error": str(e)
        }


async def run_benchmark(agent_path: Path, results_dir: Path) -> None:
    """Run diverse benchmark scenarios"""

    # Create results directory
    results_dir.mkdir(parents=True, exist_ok=True)

    # Define diverse test scenarios with specific queries
    scenarios = [
        {
            "name": "file_discovery",
            "query": "Find all Python files in the project and tell me what the main entry points are."
        },
        {
            "name": "config_analysis",
            "query": "Look for configuration files (like .yaml, .json, .toml) and summarize what they configure."
        },
        {
            "name": "readme_comprehension",
            "query": "Read the README.md file and explain what this project does and how to use it."
        },
        {
            "name": "code_structure",
            "query": "Analyze the astk directory structure and explain the main components of this codebase."
        },
        {
            "name": "documentation_search",
            "query": "Look in the docs folder and summarize what documentation is available."
        },
        {
            "name": "dependency_analysis",
            "query": "Find and analyze the requirements.txt or setup.py file to list the main dependencies."
        },
        {
            "name": "example_exploration",
            "query": "Explore the examples directory and describe what example code is available."
        },
        {
            "name": "test_discovery",
            "query": "Look for test files and describe what testing framework and test cases exist."
        }
    ]

    results = []
    total_start = time.time()

    print(f"Starting intelligent benchmark for agent: {agent_path}")
    print(f"Running {len(scenarios)} diverse scenarios...\n")

    for i, scenario in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] Testing: {scenario['name']}")
        print(f"Query: {scenario['query']}")

        result = await run_agent_scenario(agent_path, scenario['name'], scenario['query'])
        results.append(result)

        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} Duration: {result['duration_seconds']:.2f}s")

        if result["error"]:
            print(f"   Error: {result['error']}")
        elif result["success"]:
            # Show a preview of the response (first 150 chars)
            preview = result["output"].strip()[:150].replace('\n', ' ')
            print(f"   Response: {preview}...")

        print()  # Empty line for readability

    total_duration = time.time() - total_start

    # Calculate summary
    successful = sum(1 for r in results if r["success"])
    avg_duration = sum(r["duration_seconds"] for r in results) / len(results)

    # Calculate response quality metrics
    avg_response_length = sum(len(r.get("output", ""))
                              for r in results if r["success"]) / max(successful, 1)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "agent": str(agent_path),
        "total_scenarios": len(scenarios),
        "successful_scenarios": successful,
        "success_rate": successful / len(scenarios),
        "total_duration_seconds": total_duration,
        "average_scenario_duration": avg_duration,
        "average_response_length": avg_response_length,
        "scenarios": results
    }

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"intelligent_benchmark_{timestamp}.json"

    with open(result_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print("=" * 60)
    print("🎯 INTELLIGENT BENCHMARK COMPLETE!")
    print("=" * 60)
    print(
        f"✅ Success Rate: {summary['success_rate']:.1%} ({successful}/{len(scenarios)})")
    print(f"⏱️  Total Time: {total_duration:.2f}s")
    print(f"📊 Average Scenario Time: {avg_duration:.2f}s")
    print(f"📝 Average Response Length: {avg_response_length:.0f} characters")
    print(f"💾 Results saved: {result_file}")

    # Show failed scenarios if any
    failed_scenarios = [r for r in results if not r["success"]]
    if failed_scenarios:
        print(f"\n❌ Failed Scenarios ({len(failed_scenarios)}):")
        for failed in failed_scenarios:
            print(
                f"   - {failed['scenario']}: {failed.get('error', 'Unknown error')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ASTK Intelligent Benchmark Runner - Test AI agents with diverse scenarios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/simple_benchmark.py examples/agents/file_qa_agent.py
    ./scripts/simple_benchmark.py examples/agents/file_qa_agent.py
    
The benchmark runs 8 intelligent scenarios:
    📁 File Discovery     - Find Python files and entry points
    ⚙️ Config Analysis    - Analyze configuration files  
    📖 README Comprehension - Read and explain project
    🏗️ Code Structure    - Analyze directory structure
    📚 Documentation Search - Explore documentation
    🔗 Dependency Analysis - Analyze requirements/dependencies
    💡 Example Exploration - Discover example code
    🧪 Test Discovery     - Find testing framework

Results are saved to benchmark_results/ directory.
        """
    )

    parser.add_argument(
        "agent_path",
        help="Path to the agent script to benchmark"
    )

    parser.add_argument(
        "--results-dir",
        default="benchmark_results",
        help="Directory to save results (default: benchmark_results)"
    )

    args = parser.parse_args()

    agent_path = Path(args.agent_path)
    if not agent_path.exists():
        print(f"❌ Error: Agent file not found: {agent_path}")
        print("\nAvailable example agents:")
        print("  📁 examples/agents/file_qa_agent.py - LangChain File Q&A agent")
        sys.exit(1)

    results_dir = Path(args.results_dir)

    print("🚀 ASTK Intelligent Benchmark Runner")
    print(f"Agent: {agent_path}")
    print(f"Results: {results_dir}")
    print()

    asyncio.run(run_benchmark(agent_path, results_dir))
