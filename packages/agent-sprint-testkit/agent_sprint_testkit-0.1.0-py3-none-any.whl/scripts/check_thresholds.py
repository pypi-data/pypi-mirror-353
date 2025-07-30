#!/usr/bin/env python3
"""
Script to check benchmark results against configured thresholds with advanced analytics
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
from scipy import stats
import numpy as np
import yaml
import click
from tabulate import tabulate
import matplotlib.pyplot as plt
from astk.benchmarks.visualization import BenchmarkVisualizer


class ThresholdViolation:
    def __init__(self, metric: str, value: float, threshold: float, is_warning: bool, significance: Optional[float] = None):
        self.metric = metric
        self.value = value
        self.threshold = threshold
        self.is_warning = is_warning
        self.significance = significance

    def __str__(self):
        level = "WARNING" if self.is_warning else "ERROR"
        sig_str = f" (p={self.significance:.3f})" if self.significance is not None else ""
        return f"{level}: {self.metric} = {self.value:.2f} (threshold: {self.threshold:.2f}){sig_str}"


class BenchmarkAnalyzer:
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.baseline_cache = {}

    def load_historical_data(self, scenario_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Load historical benchmark results for trend analysis"""
        cutoff = datetime.now() - timedelta(days=days)
        results = []

        for file in self.history_dir.glob("benchmark_results_*.json"):
            try:
                # Extract date from filename
                date_str = file.stem.split("_")[2]
                date = datetime.strptime(date_str, "%Y%m%d")

                if date >= cutoff:
                    data = json.loads(file.read_text())
                    for result in data["results"]:
                        if result["scenario_name"] == scenario_name:
                            result["date"] = date
                            results.append(result)
            except (ValueError, KeyError, json.JSONDecodeError):
                continue

        return sorted(results, key=lambda x: x["date"])

    def get_baseline_stats(self, scenario_name: str) -> Dict[str, Dict[str, float]]:
        """Get baseline statistics from historical data"""
        if scenario_name in self.baseline_cache:
            return self.baseline_cache[scenario_name]

        historical_data = self.load_historical_data(scenario_name)
        if not historical_data:
            return {}

        # Calculate baseline stats for each metric
        baseline = {}
        metrics_to_analyze = [
            ("error_rate", None),
            ("latency.p50", "latency"),
            ("latency.p95", "latency"),
            ("throughput.conversations_per_minute", "throughput"),
            ("resources.total_tokens", "resources"),
            ("coverage_percentage", None)
        ]

        for metric_path, category in metrics_to_analyze:
            values = []
            for result in historical_data:
                try:
                    value = result
                    for key in metric_path.split("."):
                        value = value[key]
                    values.append(value)
                except KeyError:
                    continue

            if values:
                baseline[metric_path] = {
                    "mean": statistics.mean(values),
                    "stddev": statistics.stdev(values) if len(values) > 1 else 0,
                    "trend": self.calculate_trend(values)
                }

        self.baseline_cache[scenario_name] = baseline
        return baseline

    def calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression"""
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        slope, _, _, _, _ = stats.linregress(x, values)
        return slope

    def plot_trend(self, scenario_name: str, metric_path: str, output_dir: Path) -> Optional[str]:
        """Generate trend plot for a metric"""
        historical_data = self.load_historical_data(scenario_name)
        if not historical_data:
            return None

        dates = [r["date"] for r in historical_data]
        values = []
        for result in historical_data:
            try:
                value = result
                for key in metric_path.split("."):
                    value = value[key]
                values.append(value)
            except KeyError:
                continue

        if not values:
            return None

        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, marker='o')
        plt.title(f"{scenario_name} - {metric_path} Trend")
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_file = output_dir / \
            f"{scenario_name}_{metric_path.replace('.', '_')}_trend.png"
        plt.savefig(output_file)
        plt.close()

        return str(output_file)


def check_numeric_threshold(
    value: float,
    thresholds: Dict[str, float],
    metric: str,
    is_minimum: bool = False,
    baseline_stats: Optional[Dict[str, float]] = None
) -> List[ThresholdViolation]:
    violations = []

    # Absolute threshold checks
    if is_minimum:
        if "min" in thresholds and value < thresholds["min"]:
            violations.append(ThresholdViolation(
                metric, value, thresholds["min"], False))
        elif "warning" in thresholds and value < thresholds["warning"]:
            violations.append(ThresholdViolation(
                metric, value, thresholds["warning"], True))
    else:
        if "max" in thresholds and value > thresholds["max"]:
            violations.append(ThresholdViolation(
                metric, value, thresholds["max"], False))
        elif "warning" in thresholds and value > thresholds["warning"]:
            violations.append(ThresholdViolation(
                metric, value, thresholds["warning"], True))

    # Relative threshold checks against baseline
    if baseline_stats:
        baseline_mean = baseline_stats.get("mean")
        baseline_stddev = baseline_stats.get("stddev")
        if baseline_mean is not None and baseline_stddev is not None:
            z_score = (value - baseline_mean) / \
                baseline_stddev if baseline_stddev > 0 else 0
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

            # Check for significant degradation
            if p_value < 0.05 and (
                (is_minimum and value < baseline_mean) or
                (not is_minimum and value > baseline_mean)
            ):
                violations.append(ThresholdViolation(
                    f"{metric}_baseline",
                    value,
                    baseline_mean,
                    True,
                    p_value
                ))

    return violations


def check_scenario_thresholds(
    result: Dict[str, Any],
    thresholds: Dict[str, Any],
    analyzer: BenchmarkAnalyzer,
    scenario_overrides: Optional[Dict[str, Any]] = None
) -> Tuple[List[ThresholdViolation], Dict[str, Any]]:
    violations = []
    metrics_summary = {}

    # Get baseline stats
    baseline_stats = analyzer.get_baseline_stats(result["scenario_name"])

    # Apply scenario-specific overrides if they exist
    scenario_name = result["scenario_name"]
    if scenario_overrides and scenario_name in scenario_overrides:
        thresholds = {**thresholds}  # Create a copy
        for metric, override in scenario_overrides[scenario_name].items():
            if metric in thresholds:
                thresholds[metric] = {**thresholds[metric], **override}

    # Check error rate
    violations.extend(check_numeric_threshold(
        result["error_rate"],
        thresholds["error_rate"],
        "error_rate",
        baseline_stats=baseline_stats.get("error_rate")
    ))
    metrics_summary["error_rate"] = result["error_rate"]

    # Check latency metrics
    for percentile in ["p50", "p90", "p95", "p99"]:
        if percentile in thresholds["latency"]:
            metric_path = f"latency.{percentile}"
            violations.extend(check_numeric_threshold(
                result["latency"][percentile],
                thresholds["latency"][percentile],
                f"latency_{percentile}",
                baseline_stats=baseline_stats.get(metric_path)
            ))
            metrics_summary[f"latency_{percentile}"] = result["latency"][percentile]

    # Check throughput metrics
    for metric in ["conversations_per_minute", "messages_per_minute"]:
        metric_path = f"throughput.{metric}"
        violations.extend(check_numeric_threshold(
            result["throughput"][metric],
            thresholds["throughput"][metric],
            f"throughput_{metric}",
            is_minimum=True,
            baseline_stats=baseline_stats.get(metric_path)
        ))
        metrics_summary[f"throughput_{metric}"] = result["throughput"][metric]

    # Check resource metrics
    for metric in ["peak_memory_mb", "total_tokens", "total_cost_usd"]:
        metric_path = f"resources.{metric}"
        violations.extend(check_numeric_threshold(
            result["resources"][metric],
            thresholds["resources"][metric],
            f"resources_{metric}",
            baseline_stats=baseline_stats.get(metric_path)
        ))
        metrics_summary[f"resources_{metric}"] = result["resources"][metric]

    # Check coverage
    violations.extend(check_numeric_threshold(
        result["coverage_percentage"],
        thresholds["coverage"],
        "coverage",
        is_minimum=True,
        baseline_stats=baseline_stats.get("coverage_percentage")
    ))
    metrics_summary["coverage"] = result["coverage_percentage"]

    return violations, metrics_summary


def generate_markdown_report(
    scenario_results: List[Tuple[str, List[ThresholdViolation], Dict[str, Any]]],
    analyzer: BenchmarkAnalyzer,
    visualizer: BenchmarkVisualizer,
    output_dir: Path
) -> str:
    """Generate a detailed Markdown report for PR comments"""
    report = ["# Benchmark Results Summary\n"]

    for scenario_name, violations, metrics in scenario_results:
        report.append(f"## {scenario_name}\n")

        # Add metrics table
        metrics_table = []
        baseline_stats = analyzer.get_baseline_stats(scenario_name)

        for metric, value in metrics.items():
            baseline = baseline_stats.get(metric, {})
            baseline_mean = baseline.get("mean", "N/A")
            trend = baseline.get("trend", 0.0)

            trend_indicator = "↗️" if trend > 0 else "↘️" if trend < 0 else "➡️"
            metrics_table.append([
                metric,
                f"{value:.2f}",
                f"{baseline_mean:.2f}" if baseline_mean != "N/A" else "N/A",
                trend_indicator
            ])

        report.append("### Metrics\n")
        report.append(tabulate(
            metrics_table,
            headers=["Metric", "Value", "Baseline", "Trend"],
            tablefmt="pipe"
        ))
        report.append("\n")

        # Add violations
        if violations:
            report.append("### Violations\n")
            for v in violations:
                report.append(f"- {str(v)}\n")
        else:
            report.append("### ✅ All checks passed\n")

        report.append("\n### 📊 Detailed Analysis\n")
        report.append(
            f"[View Interactive Dashboard]({output_dir}/benchmark_report.html)\n")
        report.append("---\n")

    return "\n".join(report)


@click.command()
@click.option(
    "--results-file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to benchmark results JSON file"
)
@click.option(
    "--thresholds-file",
    type=click.Path(exists=True, path_type=Path),
    default=Path("config/benchmark_thresholds.yaml"),
    help="Path to thresholds configuration YAML"
)
@click.option(
    "--history-dir",
    type=click.Path(exists=True, path_type=Path),
    default=Path("benchmark_results"),
    help="Directory containing historical benchmark results"
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("benchmark_reports"),
    help="Directory to save reports and plots"
)
@click.option(
    "--fail-on-warning",
    is_flag=True,
    help="Exit with error on warning-level violations"
)
@click.option(
    "--markdown-report",
    is_flag=True,
    help="Generate detailed Markdown report"
)
def main(
    results_file: Path,
    thresholds_file: Path,
    history_dir: Path,
    output_dir: Path,
    fail_on_warning: bool,
    markdown_report: bool
) -> None:
    """Check benchmark results against configured thresholds with advanced analytics"""

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize analyzer and visualizer
    analyzer = BenchmarkAnalyzer(history_dir)
    visualizer = BenchmarkVisualizer(output_dir)

    # Load results and thresholds
    results = json.loads(results_file.read_text())
    config = yaml.safe_load(thresholds_file.read_text())

    all_violations = []
    error_found = False
    scenario_results = []

    # Check each scenario result
    for result in results["results"]:
        violations, metrics_summary = check_scenario_thresholds(
            result,
            config["thresholds"],
            analyzer,
            config.get("scenario_overrides")
        )

        scenario_results.append(
            (result["scenario_name"], violations, metrics_summary))

        if violations:
            click.echo(
                f"\nViolations for scenario '{result['scenario_name']}':")
            for v in violations:
                click.echo(f"  {v}")
                if not v.is_warning or fail_on_warning:
                    error_found = True
            all_violations.extend(violations)

    # Generate reports
    if markdown_report:
        # Generate interactive HTML report
        historical_data = {
            name: analyzer.load_historical_data(name)
            for name, _, _ in scenario_results
        }
        visualizer.save_html_report(
            [results["results"][i] for i in range(len(scenario_results))],
            historical_data,
            config["thresholds"]
        )

        # Generate Markdown report
        report = generate_markdown_report(
            scenario_results,
            analyzer,
            visualizer,
            output_dir
        )
        report_file = output_dir / "benchmark_report.md"
        report_file.write_text(report)
        click.echo(f"\nDetailed reports saved to {output_dir}")

    if not all_violations:
        click.echo("\nAll checks passed successfully!")
    elif error_found:
        sys.exit(1)


if __name__ == "__main__":
    main()
