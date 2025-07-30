"""
Benchmark runner for executing performance tests
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import psutil
import yaml
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..runner import AgentRunner
from ..schema import ScenarioConfig
from .metrics import MetricsCollector, BenchmarkResult


class BenchmarkRunner:
    """Executes benchmark scenarios and collects metrics"""

    def __init__(
        self,
        scenarios_dir: Union[str, Path],
        results_dir: Union[str, Path],
        agent_entrypoint: Union[str, Path],
        docker_image: Optional[str] = None,
        parallel: bool = True
    ):
        self.scenarios_dir = Path(scenarios_dir)
        self.results_dir = Path(results_dir)
        self.agent_entrypoint = Path(agent_entrypoint)
        self.docker_image = docker_image
        self.parallel = parallel

        # Create results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize tracing
        self.tracer = trace.get_tracer("astk.benchmarks")

    async def run_scenario(
        self,
        scenario_file: Path,
        collector: MetricsCollector
    ) -> None:
        """
        Run a single benchmark scenario

        Args:
            scenario_file: Path to scenario YAML
            collector: Metrics collector instance
        """
        with self.tracer.start_as_current_span("benchmark_scenario") as span:
            try:
                # Run scenario
                runner = AgentRunner(
                    self.agent_entrypoint,
                    scenario_file,
                    self.docker_image
                )
                results = await runner.run_scenarios()

                # Record metrics
                for conv in results["conversations"]:
                    collector.record_conversation()
                    for msg in conv["messages"]:
                        if msg.get("metadata", {}).get("latency_ms"):
                            collector.record_message_latency(
                                msg["metadata"]["latency_ms"]
                            )

                    # Record any errors
                    if not conv["passed"]:
                        collector.record_error()

                # Record resource usage
                process = psutil.Process()
                collector.record_resource_usage(
                    tokens=results.get("total_tokens", 0),
                    cost_usd=results.get("total_cost", 0.0),
                    memory_mb=process.memory_info().rss / 1024 / 1024
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR), str(e))
                raise

    async def run_benchmarks(self) -> List[BenchmarkResult]:
        """
        Run all benchmark scenarios

        Returns:
            List of benchmark results
        """
        # Find all scenario files
        scenario_files = list(self.scenarios_dir.glob("*.yaml"))
        if not scenario_files:
            raise ValueError(
                f"No scenario files found in {self.scenarios_dir}")

        results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for scenario_file in scenario_files:
            # Create metrics collector
            collector = MetricsCollector()

            # Run scenario
            await self.run_scenario(scenario_file, collector)

            # Compute and save results
            scenario_name = scenario_file.stem
            result = collector.compute_results(scenario_name)
            results.append(result)

            # Save individual result
            result_file = self.results_dir / \
                f"{scenario_name}_{timestamp}.json"
            result_file.write_text(result.model_dump_json(indent=2))

        # Save combined results
        combined_file = self.results_dir / \
            f"benchmark_results_{timestamp}.json"
        combined_results = {
            "timestamp": timestamp,
            "results": [r.model_dump() for r in results]
        }
        combined_file.write_text(json.dumps(combined_results, indent=2))

        return results

    @classmethod
    async def execute(
        cls,
        scenarios_dir: Union[str, Path],
        results_dir: Union[str, Path],
        agent_entrypoint: Union[str, Path],
        docker_image: Optional[str] = None,
        parallel: bool = True
    ) -> List[BenchmarkResult]:
        """
        Factory method to create runner and execute benchmarks

        Args:
            scenarios_dir: Directory containing scenario YAML files
            results_dir: Directory to save results
            agent_entrypoint: Path to agent entry point
            docker_image: Optional Docker image to run agent in
            parallel: Whether to run scenarios in parallel

        Returns:
            List of benchmark results
        """
        runner = cls(
            scenarios_dir,
            results_dir,
            agent_entrypoint,
            docker_image,
            parallel
        )
        return await runner.run_benchmarks()
