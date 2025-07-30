#!/usr/bin/env python3
"""
ASTK CLI - Run benchmarks and view results
"""

import click
import sys
import webbrowser
from pathlib import Path
import subprocess
import yaml
from typing import Optional


def ensure_directory(path: Path) -> None:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)


def validate_config(config_path: Path) -> bool:
    """Validate benchmark configuration"""
    try:
        with open(config_path) as f:
            yaml.safe_load(f)
        return True
    except Exception as e:
        click.echo(f"Error in config file: {e}", err=True)
        return False


@click.group()
def cli():
    """AgentSprint TestKit (ASTK) - Benchmark your AI agents"""
    pass


@cli.command()
@click.argument('agent_path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--scenarios-dir',
    type=click.Path(exists=True, path_type=Path),
    default=Path("examples/benchmarks/scenarios"),
    help="Directory containing benchmark scenarios"
)
@click.option(
    '--results-dir',
    type=click.Path(path_type=Path),
    default=Path("benchmark_results"),
    help="Directory to save results"
)
@click.option(
    '--thresholds-file',
    type=click.Path(exists=True, path_type=Path),
    default=Path("config/benchmark_thresholds.yaml"),
    help="Path to thresholds configuration"
)
@click.option(
    '--docker-image',
    help="Optional Docker image to run agent in"
)
@click.option(
    '--fail-on-warning',
    is_flag=True,
    help="Exit with error on warning-level violations"
)
def run(
    agent_path: Path,
    scenarios_dir: Path,
    results_dir: Path,
    thresholds_file: Path,
    docker_image: Optional[str],
    fail_on_warning: bool
):
    """Run benchmarks on an agent"""

    # Ensure directories exist
    ensure_directory(results_dir)

    # Validate config
    if not validate_config(thresholds_file):
        sys.exit(1)

    click.echo("Starting benchmark run...")
    click.echo(f"Agent: {agent_path}")
    click.echo(f"Scenarios: {scenarios_dir}")

    try:
        # Run benchmarks
        cmd = [
            sys.executable,
            "scripts/run_benchmarks.py",
            "--agent-entrypoint", str(agent_path),
            "--scenarios-dir", str(scenarios_dir),
            "--results-dir", str(results_dir),
            "--thresholds-file", str(thresholds_file),
            "--markdown-report"
        ]

        if docker_image:
            cmd.extend(["--docker-image", docker_image])
        if fail_on_warning:
            cmd.append("--fail-on-warning")

        result = subprocess.run(cmd, check=True)

        # Open results in browser
        report_path = results_dir / "benchmark_reports/benchmark_report.html"
        if report_path.exists():
            click.echo("\nOpening results in browser...")
            webbrowser.open(f"file://{report_path.absolute()}")

        click.echo("\nBenchmark run completed successfully!")

    except subprocess.CalledProcessError as e:
        click.echo(f"\nError running benchmarks: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('results_dir', type=click.Path(exists=True, path_type=Path))
def view(results_dir: Path):
    """View benchmark results"""
    report_path = results_dir / "benchmark_reports/benchmark_report.html"
    if report_path.exists():
        click.echo("Opening results in browser...")
        webbrowser.open(f"file://{report_path.absolute()}")
    else:
        click.echo("No benchmark report found. Run benchmarks first.", err=True)
        sys.exit(1)


@cli.command()
def init():
    """Initialize ASTK in current directory"""
    # Create directory structure
    dirs = [
        "examples/benchmarks/scenarios",
        "config",
        "benchmark_results",
        "benchmark_reports"
    ]
    for d in dirs:
        ensure_directory(Path(d))

    # Create example scenario
    example_scenario = """
task: "file_qna"
persona:
  archetype: "impatient_mobile_user"
  temperature: 0.9
  traits:
    - "demanding"
    - "tech-savvy"
protocol: "A2A"
success:
  regex: "(?i)here's"
  semantic_score: 0.8
budgets:
  latency_ms: 3000
  cost_usd: 0.1
  tokens: 1000
chaos:
  drop_tool:
    - "search"
    - "memory"
  inject_latency:
    - 500
    - 1000
  malform_messages: true
    """

    # Create example threshold config
    example_thresholds = """
thresholds:
  error_rate:
    max: 0.1
    warning: 0.05
  latency:
    p95:
      max: 5000
      warning: 4000
  throughput:
    conversations_per_minute:
      min: 10
      warning: 15
  coverage:
    min: 80
    warning: 90
    """

    # Write example files
    (Path("examples/benchmarks/scenarios/example.yaml")
        .write_text(example_scenario.strip()))
    (Path("config/benchmark_thresholds.yaml")
        .write_text(example_thresholds.strip()))

    click.echo("Initialized ASTK with example configuration!")
    click.echo("\nDirectory structure created:")
    click.echo("  examples/benchmarks/scenarios/ - Benchmark scenarios")
    click.echo("  config/                       - Configuration files")
    click.echo("  benchmark_results/            - Benchmark results")
    click.echo("  benchmark_reports/            - Generated reports")
    click.echo("\nExample files created:")
    click.echo("  examples/benchmarks/scenarios/example.yaml - Example scenario")
    click.echo("  config/benchmark_thresholds.yaml          - Example thresholds")
    click.echo("\nRun 'astk run <agent_path>' to start benchmarking!")


if __name__ == "__main__":
    cli()
