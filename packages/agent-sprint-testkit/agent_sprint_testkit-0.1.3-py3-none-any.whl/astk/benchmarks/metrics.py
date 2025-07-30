"""
Benchmark metrics for ASTK performance measurement
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import statistics
from pydantic import BaseModel


class LatencyMetrics(BaseModel):
    """Latency measurements in milliseconds"""
    mean: float
    p50: float
    p90: float
    p95: float
    p99: float


class ThroughputMetrics(BaseModel):
    """Throughput measurements"""
    conversations_per_minute: float
    messages_per_minute: float


class ResourceMetrics(BaseModel):
    """Resource usage measurements"""
    peak_memory_mb: float
    total_tokens: int
    total_cost_usd: float


class BenchmarkResult(BaseModel):
    """Complete benchmark results"""
    scenario_name: str
    num_conversations: int
    num_messages: int
    duration_seconds: float
    latency: LatencyMetrics
    throughput: ThroughputMetrics
    resources: ResourceMetrics
    error_rate: float
    coverage_percentage: float


class MetricsCollector:
    """Collects and computes benchmark metrics"""

    def __init__(self):
        self.start_time = time.time()
        self.message_latencies: List[float] = []
        self.total_messages = 0
        self.total_conversations = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.peak_memory = 0.0
        self.errors = 0
        self.coverage_hits = 0
        self.coverage_total = 0

    def record_message_latency(self, latency_ms: float) -> None:
        """Record a message latency measurement"""
        self.message_latencies.append(latency_ms)
        self.total_messages += 1

    def record_conversation(self) -> None:
        """Record completion of a conversation"""
        self.total_conversations += 1

    def record_resource_usage(
        self,
        tokens: int,
        cost_usd: float,
        memory_mb: float
    ) -> None:
        """Record resource usage metrics"""
        self.total_tokens += tokens
        self.total_cost += cost_usd
        self.peak_memory = max(self.peak_memory, memory_mb)

    def record_error(self) -> None:
        """Record an error occurrence"""
        self.errors += 1

    def record_coverage(self, hits: int, total: int) -> None:
        """Record coverage metrics"""
        self.coverage_hits += hits
        self.coverage_total += total

    def compute_results(self, scenario_name: str) -> BenchmarkResult:
        """Compute final benchmark results"""
        duration = time.time() - self.start_time

        # Compute latency percentiles
        sorted_latencies = sorted(self.message_latencies)
        latency = LatencyMetrics(
            mean=statistics.mean(sorted_latencies),
            p50=statistics.median(sorted_latencies),
            p90=statistics.quantiles(sorted_latencies, n=10)[-1],
            p95=statistics.quantiles(sorted_latencies, n=20)[-1],
            p99=statistics.quantiles(sorted_latencies, n=100)[-1]
        )

        # Compute throughput
        minutes = duration / 60
        throughput = ThroughputMetrics(
            conversations_per_minute=self.total_conversations / minutes,
            messages_per_minute=self.total_messages / minutes
        )

        # Compute resource metrics
        resources = ResourceMetrics(
            peak_memory_mb=self.peak_memory,
            total_tokens=self.total_tokens,
            total_cost_usd=self.total_cost
        )

        # Compute error rate and coverage
        error_rate = self.errors / self.total_messages if self.total_messages > 0 else 0
        coverage = (self.coverage_hits / self.coverage_total *
                    100) if self.coverage_total > 0 else 0

        return BenchmarkResult(
            scenario_name=scenario_name,
            num_conversations=self.total_conversations,
            num_messages=self.total_messages,
            duration_seconds=duration,
            latency=latency,
            throughput=throughput,
            resources=resources,
            error_rate=error_rate,
            coverage_percentage=coverage
        )
