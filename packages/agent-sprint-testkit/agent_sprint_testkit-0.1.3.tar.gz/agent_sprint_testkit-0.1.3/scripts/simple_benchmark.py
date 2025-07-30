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

    # Define sophisticated test scenarios with advanced queries
    scenarios = [
        {
            "name": "multi_step_reasoning",
            "query": "Given this codebase, identify potential security vulnerabilities in the file handling. Then explain how an attacker might exploit them and suggest specific fixes with code examples.",
            "category": "reasoning",
            "difficulty": "advanced"
        },
        {
            "name": "creative_problem_solving",
            "query": "Imagine you need to add real-time collaboration features to this project. Design a complete architecture including websockets, conflict resolution, and user presence indicators. Provide implementation details.",
            "category": "creativity",
            "difficulty": "expert"
        },
        {
            "name": "edge_case_analysis",
            "query": "What happens if someone tries to benchmark an agent that doesn't exist, takes 10 minutes to respond, or returns binary data? How should the system handle these edge cases?",
            "category": "edge_cases",
            "difficulty": "intermediate"
        },
        {
            "name": "performance_optimization",
            "query": "Analyze the benchmark runner code and identify performance bottlenecks. Suggest specific optimizations for handling 1000+ concurrent agent tests with detailed implementation strategies.",
            "category": "optimization",
            "difficulty": "advanced"
        },
        {
            "name": "cross_domain_integration",
            "query": "How would you integrate this testing framework with CI/CD pipelines, monitoring systems, and cloud deployment? Provide a complete DevOps strategy with example configurations.",
            "category": "integration",
            "difficulty": "expert"
        },
        {
            "name": "failure_recovery_design",
            "query": "Design a comprehensive error handling and recovery system for agent failures. Include retry strategies, circuit breakers, graceful degradation, and user notifications with pseudocode.",
            "category": "reliability",
            "difficulty": "advanced"
        },
        {
            "name": "scalability_architecture",
            "query": "Redesign this system to handle 100,000 agents being tested simultaneously across multiple data centers. Address load balancing, data consistency, and resource management.",
            "category": "scalability",
            "difficulty": "expert"
        },
        {
            "name": "ethical_ai_evaluation",
            "query": "Propose methods to test AI agents for bias, fairness, and ethical decision-making. Include specific test scenarios for detecting harmful outputs and ensuring responsible AI behavior.",
            "category": "ethics",
            "difficulty": "advanced"
        },
        {
            "name": "adaptive_learning_assessment",
            "query": "Design a system where the testing framework learns from agent responses and automatically generates more challenging scenarios. How would this self-improving test system work?",
            "category": "ml_advanced",
            "difficulty": "expert"
        },
        {
            "name": "competitive_analysis",
            "query": "Compare this framework with existing agent testing solutions. Identify unique value propositions, competitive advantages, and market positioning strategy with detailed analysis.",
            "category": "business",
            "difficulty": "intermediate"
        },
        {
            "name": "quantum_computing_readiness",
            "query": "How would you prepare this testing framework for quantum-powered AI agents? Address quantum-specific challenges, testing methodologies, and performance metrics.",
            "category": "future_tech",
            "difficulty": "expert"
        },
        {
            "name": "regulatory_compliance",
            "query": "Ensure this framework complies with GDPR, CCPA, and emerging AI regulations. Design audit trails, data governance, and compliance reporting features with implementation details.",
            "category": "compliance",
            "difficulty": "advanced"
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

    # Calculate sophisticated metrics
    difficulty_performance = {}
    category_performance = {}

    for i, result in enumerate(results):
        scenario = scenarios[i]
        difficulty = scenario.get("difficulty", "unknown")
        category = scenario.get("category", "unknown")

        # Track performance by difficulty
        if difficulty not in difficulty_performance:
            difficulty_performance[difficulty] = {"total": 0, "success": 0}
        difficulty_performance[difficulty]["total"] += 1
        if result["success"]:
            difficulty_performance[difficulty]["success"] += 1

        # Track performance by category
        if category not in category_performance:
            category_performance[category] = {"total": 0, "success": 0}
        category_performance[category]["total"] += 1
        if result["success"]:
            category_performance[category]["success"] += 1

    # Calculate complexity score (weighted by difficulty)
    difficulty_weights = {"intermediate": 1, "advanced": 2, "expert": 3}
    total_complexity_points = sum(difficulty_weights.get(scenarios[i].get("difficulty", "intermediate"), 1)
                                  for i in range(len(scenarios)))
    earned_complexity_points = sum(difficulty_weights.get(scenarios[i].get("difficulty", "intermediate"), 1)
                                   for i, r in enumerate(results) if r["success"])
    complexity_score = earned_complexity_points / \
        total_complexity_points if total_complexity_points > 0 else 0

    summary = {
        "timestamp": datetime.now().isoformat(),
        "agent": str(agent_path),
        "total_scenarios": len(scenarios),
        "successful_scenarios": successful,
        "success_rate": successful / len(scenarios),
        "complexity_score": complexity_score,
        "total_duration_seconds": total_duration,
        "average_scenario_duration": avg_duration,
        "average_response_length": avg_response_length,
        "difficulty_breakdown": {
            diff: {
                "success_rate": data["success"] / data["total"],
                "scenarios": f"{data['success']}/{data['total']}"
            }
            for diff, data in difficulty_performance.items()
        },
        "category_breakdown": {
            cat: {
                "success_rate": data["success"] / data["total"],
                "scenarios": f"{data['success']}/{data['total']}"
            }
            for cat, data in category_performance.items()
        },
        "scenarios": results
    }

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"intelligent_benchmark_{timestamp}.json"

    with open(result_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print("=" * 60)
    print("🎯 SOPHISTICATED AI BENCHMARK COMPLETE!")
    print("=" * 60)
    print(
        f"✅ Success Rate: {summary['success_rate']:.1%} ({successful}/{len(scenarios)})")
    print(
        f"🧠 Complexity Score: {summary['complexity_score']:.1%} (difficulty-weighted)")
    print(f"⏱️  Total Time: {total_duration:.2f}s")
    print(f"📊 Average Scenario Time: {avg_duration:.2f}s")
    print(f"📝 Average Response Length: {avg_response_length:.0f} characters")

    # Show difficulty breakdown
    print(f"\n🎓 Performance by Difficulty:")
    for difficulty, stats in summary['difficulty_breakdown'].items():
        emoji = {"intermediate": "📘", "advanced": "📙",
                 "expert": "📕"}.get(difficulty, "📗")
        print(
            f"   {emoji} {difficulty.title()}: {stats['success_rate']:.1%} ({stats['scenarios']})")

    # Show category breakdown
    print(f"\n🏷️  Performance by Category:")
    category_emojis = {
        "reasoning": "🧠", "creativity": "🎨", "edge_cases": "⚠️",
        "optimization": "⚡", "integration": "🔗", "reliability": "🛡️",
        "scalability": "📈", "ethics": "⚖️", "ml_advanced": "🤖",
        "business": "💼", "future_tech": "🚀", "compliance": "📋"
    }
    for category, stats in summary['category_breakdown'].items():
        emoji = category_emojis.get(category, "📂")
        print(
            f"   {emoji} {category.replace('_', ' ').title()}: {stats['success_rate']:.1%} ({stats['scenarios']})")

    print(f"\n💾 Results saved: {result_file}")

    # Show failed scenarios if any
    failed_scenarios = [r for r in results if not r["success"]]
    if failed_scenarios:
        print(f"\n❌ Failed Scenarios ({len(failed_scenarios)}):")
        for i, failed in enumerate(failed_scenarios):
            scenario_info = scenarios[next(j for j, s in enumerate(
                scenarios) if s["name"] == failed["scenario"])]
            difficulty_emoji = {"intermediate": "📘", "advanced": "📙", "expert": "📕"}.get(
                scenario_info.get("difficulty"), "📗")
            print(
                f"   {difficulty_emoji} {failed['scenario']}: {failed.get('error', 'Unknown error')}")

    # Show top performing categories
    if category_performance:
        top_category = max(category_performance.items(),
                           key=lambda x: x[1]["success"] / x[1]["total"])
        if top_category[1]["success"] > 0:
            emoji = category_emojis.get(top_category[0], "📂")
            print(
                f"\n🏆 Best Category: {emoji} {top_category[0].replace('_', ' ').title()} ({top_category[1]['success']}/{top_category[1]['total']})")

    # Show AI capability assessment
    if summary['complexity_score'] >= 0.8:
        print(f"\n🌟 EXCEPTIONAL AI: This agent demonstrates expert-level reasoning across multiple domains!")
    elif summary['complexity_score'] >= 0.6:
        print(f"\n🔥 ADVANCED AI: Strong performance on sophisticated reasoning tasks!")
    elif summary['complexity_score'] >= 0.4:
        print(f"\n💡 COMPETENT AI: Good basic capabilities with room for advanced reasoning improvement.")
    else:
        print(f"\n📚 DEVELOPING AI: Focus on improving reasoning and problem-solving capabilities.")


def main():
    """Main entry point for console script"""
    parser = argparse.ArgumentParser(
        description="ASTK Sophisticated AI Benchmark Runner - Test AI agents with advanced reasoning scenarios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    astk examples/agents/file_qa_agent.py
    astk-benchmark examples/agents/file_qa_agent.py
    
The benchmark runs 12 sophisticated scenarios across multiple categories:

🧠 Reasoning & Problem-Solving:
    Multi-step reasoning, Edge case analysis, Performance optimization
    
🎨 Creativity & Innovation:  
    Creative problem solving, Adaptive learning assessment
    
🔗 System Integration:
    Cross-domain integration, Failure recovery design, Scalability architecture
    
⚖️ Ethics & Compliance:
    Ethical AI evaluation, Regulatory compliance
    
💼 Strategic Analysis:
    Competitive analysis, Quantum computing readiness

Difficulty Levels: 📘 Intermediate | 📙 Advanced | 📕 Expert

Results include complexity scores, category breakdowns, and AI capability assessments.
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


if __name__ == "__main__":
    main()
