#!/usr/bin/env python3
"""
Benchmark runner script for CI
"""

from datetime import datetime
import click
import json
import asyncio
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from astk.benchmarks.runner import BenchmarkRunner
import sys
from pathlib import Path

# Add project root to Python path before any astk imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_telemetry(otlp_endpoint: str) -> None:
    """Set up OpenTelemetry with OTLP export"""
    provider = TracerProvider()

    # Add OTLP exporter
    otlp_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=otlp_endpoint))
    provider.add_span_processor(otlp_processor)

    # Also log to console for CI visibility
    console_processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(console_processor)

    trace.set_tracer_provider(provider)


@click.command()
@click.option(
    "--scenarios-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("examples/benchmarks/scenarios"),
    help="Directory containing benchmark scenarios"
)
@click.option(
    "--results-dir",
    type=click.Path(path_type=Path),
    default=Path("benchmark_results"),
    help="Directory to save results"
)
@click.option(
    "--agent-entrypoint",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to agent entry point"
)
@click.option(
    "--docker-image",
    help="Docker image to run agent in"
)
@click.option(
    "--otlp-endpoint",
    default="localhost:4317",
    help="OTLP endpoint for telemetry"
)
@click.option(
    "--parallel/--sequential",
    default=True,
    help="Run scenarios in parallel"
)
@click.option(
    "--fail-threshold",
    type=float,
    default=0.1,
    help="Fail if error rate exceeds this value"
)
def main(
    scenarios_dir: Path,
    results_dir: Path,
    agent_entrypoint: Path,
    docker_image: str,
    otlp_endpoint: str,
    parallel: bool,
    fail_threshold: float
) -> None:
    """Run benchmark scenarios and export results"""
    # Set up telemetry
    setup_telemetry(otlp_endpoint)

    try:
        # Run benchmarks
        results = asyncio.run(
            BenchmarkRunner.execute(
                scenarios_dir=scenarios_dir,
                results_dir=results_dir,
                agent_entrypoint=agent_entrypoint,
                docker_image=docker_image,
                parallel=parallel
            )
        )

        # Check results against thresholds
        max_error_rate = max(r.error_rate for r in results)
        if max_error_rate > fail_threshold:
            click.echo(
                f"Error rate {max_error_rate:.2%} exceeds threshold {fail_threshold:.2%}",
                err=True
            )
            sys.exit(1)

        click.echo("Benchmarks completed successfully!")

    except Exception as e:
        click.echo(f"Error running benchmarks: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
