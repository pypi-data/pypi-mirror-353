"""
Enhanced visualization capabilities for benchmark results
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats
import plotly.express as px


class BenchmarkVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'background': '#f8f9fa',
            'grid': '#e9ecef'
        }
        self.js_functions = """
        function filterMetrics() {
            const metricFilter = document.getElementById('metricFilter').value.toLowerCase();
            const dateRange = document.getElementById('dateRange').value;
            const days = parseInt(dateRange) || 30;
            const cutoff = new Date();
            cutoff.setDate(cutoff.getDate() - days);
            
            document.querySelectorAll('.metric-container').forEach(container => {
                const metricName = container.getAttribute('data-metric').toLowerCase();
                const date = new Date(container.getAttribute('data-date'));
                const show = metricName.includes(metricFilter) && date >= cutoff;
                container.style.display = show ? 'block' : 'none';
            });
        }

        function toggleView(viewType) {
            document.querySelectorAll('.view-toggle').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`#${viewType}View`).classList.add('active');
            
            document.querySelectorAll('.view-content').forEach(content => {
                content.style.display = 'none';
            });
            document.querySelector(`#${viewType}Content`).style.display = 'block';
        }

        function updateThresholds(metricName) {
            const warningInput = document.getElementById(`${metricName}Warning`);
            const errorInput = document.getElementById(`${metricName}Error`);
            const warning = parseFloat(warningInput.value);
            const error = parseFloat(errorInput.value);
            
            // Update plot annotations
            const plot = document.querySelector(`[data-metric="${metricName}"] .js-plotly-plot`);
            if (plot && plot.data) {
                Plotly.relayout(plot, {
                    shapes: [
                        {
                            type: 'line',
                            y0: warning,
                            y1: warning,
                            x0: 0,
                            x1: 1,
                            xref: 'paper',
                            line: { color: 'orange', dash: 'dot' }
                        },
                        {
                            type: 'line',
                            y0: error,
                            y1: error,
                            x0: 0,
                            x1: 1,
                            xref: 'paper',
                            line: { color: 'red', dash: 'dot' }
                        }
                    ]
                });
            }
        }

        function exportData(format) {
            const data = window.benchmarkData;
            if (format === 'csv') {
                let csv = 'Scenario,Metric,Value,Date\\n';
                Object.entries(data).forEach(([scenario, metrics]) => {
                    Object.entries(metrics).forEach(([metric, values]) => {
                        values.forEach(v => {
                            csv += `${scenario},${metric},${v.value},${v.date}\\n`;
                        });
                    });
                });
                downloadFile(csv, 'benchmark_data.csv', 'text/csv');
            } else if (format === 'json') {
                downloadFile(
                    JSON.stringify(data, null, 2),
                    'benchmark_data.json',
                    'application/json'
                );
            }
        }

        function downloadFile(content, filename, type) {
            const blob = new Blob([content], { type });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        }

        function createAnnotation(event) {
            const plot = event.target.closest('.js-plotly-plot');
            const metricName = plot.closest('[data-metric]').getAttribute('data-metric');
            const note = prompt('Enter annotation:');
            if (note) {
                const annotation = {
                    x: event.xaxis.d2l(event.xaxis.clickval),
                    y: event.yaxis.d2l(event.yaxis.clickval),
                    text: note,
                    showarrow: true
                };
                Plotly.relayout(plot, {
                    annotations: plot.layout.annotations.concat([annotation])
                });
            }
        }
        """

    def create_metric_trend_plot(
        self,
        dates: List[datetime],
        values: List[float],
        baseline_mean: Optional[float],
        title: str,
        metric_name: str
    ) -> go.Figure:
        """Create an interactive trend plot with confidence intervals"""
        fig = go.Figure()

        # Add main trend line
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=metric_name,
            line=dict(color=self.color_palette['primary']),
            hovertemplate='%{x}<br>%{y:.2f}<extra></extra>'
        ))

        # Calculate and add confidence intervals if enough data points
        if len(values) > 2:
            x_numeric = np.arange(len(dates))
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x_numeric, values)

            # Calculate trend line
            trend = slope * x_numeric + intercept

            # Calculate confidence intervals
            conf_int = std_err * stats.t.ppf(0.975, len(dates)-2)
            lower_bound = trend - conf_int
            upper_bound = trend + conf_int

            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=dates + dates[::-1],
                y=np.concatenate([upper_bound, lower_bound[::-1]]),
                fill='toself',
                fillcolor=f'rgba(31, 119, 180, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip',
                showlegend=False
            ))

            # Add trend line
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend,
                mode='lines',
                name='Trend',
                line=dict(
                    color=self.color_palette['secondary'],
                    dash='dash'
                ),
                hovertemplate='Trend: %{y:.2f}<extra></extra>'
            ))

        # Add baseline if provided
        if baseline_mean is not None:
            fig.add_hline(
                y=baseline_mean,
                line_dash="dot",
                line_color=self.color_palette['success'],
                annotation_text="Baseline",
                annotation_position="bottom right"
            )

        # Update layout
        fig.update_layout(
            title=title,
            paper_bgcolor=self.color_palette['background'],
            plot_bgcolor=self.color_palette['background'],
            hovermode='x unified',
            xaxis=dict(
                showgrid=True,
                gridcolor=self.color_palette['grid'],
                title='Date'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=self.color_palette['grid'],
                title=metric_name
            )
        )

        # Add click event for annotations
        fig.update_layout(
            clickmode='event',
            hovermode='closest'
        )

        return fig

    def create_metric_distribution_plot(
        self,
        values: List[float],
        current_value: float,
        metric_name: str
    ) -> go.Figure:
        """Create a distribution plot showing historical values and current position"""
        fig = go.Figure()

        # Add histogram of historical values
        fig.add_trace(go.Histogram(
            x=values,
            name='Historical',
            nbinsx=20,
            marker_color=self.color_palette['primary']
        ))

        # Add KDE curve
        if len(values) > 2:
            kde_x = np.linspace(min(values), max(values), 100)
            kde = stats.gaussian_kde(values)
            kde_y = kde(kde_x)

            fig.add_trace(go.Scatter(
                x=kde_x,
                y=kde_y,
                mode='lines',
                name='Distribution',
                line=dict(color=self.color_palette['secondary']),
                yaxis='y2'
            ))

        # Add current value marker
        fig.add_trace(go.Scatter(
            x=[current_value],
            y=[0],
            mode='markers',
            name='Current',
            marker=dict(
                color=self.color_palette['warning'],
                size=12,
                symbol='diamond'
            )
        ))

        # Update layout
        fig.update_layout(
            title=f'{metric_name} Distribution',
            paper_bgcolor=self.color_palette['background'],
            plot_bgcolor=self.color_palette['background'],
            hovermode='x unified',
            xaxis=dict(
                showgrid=True,
                gridcolor=self.color_palette['grid'],
                title=metric_name
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=self.color_palette['grid'],
                title='Count'
            ),
            yaxis2=dict(
                showgrid=False,
                overlaying='y',
                side='right',
                title='Density'
            )
        )

        return fig

    def create_correlation_plot(
        self,
        metrics_data: Dict[str, List[float]],
        metric_names: List[str]
    ) -> go.Figure:
        """Create a correlation matrix plot between different metrics"""
        correlations = np.zeros((len(metric_names), len(metric_names)))

        for i, metric1 in enumerate(metric_names):
            for j, metric2 in enumerate(metric_names):
                if len(metrics_data[metric1]) > 1 and len(metrics_data[metric2]) > 1:
                    corr = stats.pearsonr(
                        metrics_data[metric1], metrics_data[metric2])[0]
                    correlations[i, j] = corr

        fig = go.Figure(data=go.Heatmap(
            z=correlations,
            x=metric_names,
            y=metric_names,
            colorscale='RdBu',
            zmid=0,
            text=[[f'{val:.2f}' for val in row] for row in correlations],
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))

        fig.update_layout(
            title='Metric Correlations',
            paper_bgcolor=self.color_palette['background'],
            plot_bgcolor=self.color_palette['background']
        )

        return fig

    def create_radar_plot(
        self,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float],
        thresholds: Dict[str, Dict[str, float]]
    ) -> go.Figure:
        """Create a radar plot comparing current metrics to baseline"""
        metrics = list(current_metrics.keys())

        # Normalize values between 0 and 1
        normalized_current = []
        normalized_baseline = []

        for metric in metrics:
            threshold = thresholds.get(metric, {})
            min_val = threshold.get('min', min(
                current_metrics[metric], baseline_metrics[metric]))
            max_val = threshold.get('max', max(
                current_metrics[metric], baseline_metrics[metric]))
            range_val = max_val - min_val

            if range_val > 0:
                normalized_current.append(
                    (current_metrics[metric] - min_val) / range_val)
                normalized_baseline.append(
                    (baseline_metrics[metric] - min_val) / range_val)
            else:
                normalized_current.append(0.5)
                normalized_baseline.append(0.5)

        fig = go.Figure()

        # Add baseline trace
        fig.add_trace(go.Scatterpolar(
            r=normalized_baseline,
            theta=metrics,
            fill='toself',
            name='Baseline',
            line_color=self.color_palette['secondary']
        ))

        # Add current metrics trace
        fig.add_trace(go.Scatterpolar(
            r=normalized_current,
            theta=metrics,
            fill='toself',
            name='Current',
            line_color=self.color_palette['primary']
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title='Metric Comparison',
            paper_bgcolor=self.color_palette['background']
        )

        return fig

    def generate_html_report(
        self,
        scenario_results: List[Dict[str, Any]],
        historical_data: Dict[str, List[Dict[str, Any]]],
        thresholds: Dict[str, Any]
    ) -> str:
        """Generate an interactive HTML report with enhanced features"""
        html_parts = [f"""
        <html>
        <head>
            <title>Benchmark Results</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <style>
                body {{ background-color: #f8f9fa; padding: 20px; }}
                .plot-container {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .controls {{ position: sticky; top: 0; z-index: 100; background: white; padding: 15px; border-bottom: 1px solid #dee2e6; margin-bottom: 20px; }}
                .view-toggle.active {{ background-color: #0d6efd; color: white; }}
                .threshold-control {{ margin: 10px 0; }}
                .annotation-tip {{ font-size: 0.8em; color: #6c757d; }}
            </style>
            <script>
                {self.js_functions}
            </script>
        </head>
        <body>
            <div class="container">
                <div class="controls">
                    <div class="row align-items-center">
                        <div class="col">
                            <input type="text" class="form-control" id="metricFilter" 
                                   placeholder="Filter metrics..." onkeyup="filterMetrics()">
                        </div>
                        <div class="col">
                            <select class="form-select" id="dateRange" onchange="filterMetrics()">
                                <option value="7">Last 7 days</option>
                                <option value="30" selected>Last 30 days</option>
                                <option value="90">Last 90 days</option>
                                <option value="365">Last year</option>
                            </select>
                        </div>
                        <div class="col">
                            <div class="btn-group">
                                <button class="btn btn-outline-primary view-toggle active" 
                                        id="trendView" onclick="toggleView('trend')">Trends</button>
                                <button class="btn btn-outline-primary view-toggle" 
                                        id="distributionView" onclick="toggleView('distribution')">Distributions</button>
                                <button class="btn btn-outline-primary view-toggle" 
                                        id="correlationView" onclick="toggleView('correlation')">Correlations</button>
                            </div>
                        </div>
                        <div class="col">
                            <div class="dropdown">
                                <button class="btn btn-outline-secondary dropdown-toggle" 
                                        type="button" data-bs-toggle="dropdown">
                                    Export Data
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="#" onclick="exportData('csv')">CSV</a></li>
                                    <li><a class="dropdown-item" href="#" onclick="exportData('json')">JSON</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <h1 class="mb-4">Benchmark Results</h1>
                <p class="annotation-tip">💡 Tip: Click on any plot to add annotations!</p>
        """]

        # Prepare benchmark data for export
        benchmark_data = {}
        for scenario in scenario_results:
            scenario_name = scenario["scenario_name"]
            historical = historical_data.get(scenario_name, [])

            html_parts.append(f'<h2 class="mt-5">{scenario_name}</h2>')

            # Add threshold controls
            html_parts.append("""
                <div class="threshold-control">
                    <div class="row">
                        <div class="col-md-6">
                            <label>Warning Threshold:</label>
                            <input type="number" class="form-control" 
                                   id="{metric}Warning" 
                                   value="{warning}"
                                   onchange="updateThresholds('{metric}')">
                        </div>
                        <div class="col-md-6">
                            <label>Error Threshold:</label>
                            <input type="number" class="form-control" 
                                   id="{metric}Error" 
                                   value="{error}"
                                   onchange="updateThresholds('{metric}')">
                        </div>
                    </div>
                </div>
            """)

            # Create view sections
            html_parts.append("""
                <div id="trendContent" class="view-content">
            """)

            key_metrics = ["error_rate", "latency.p95",
                           "throughput.conversations_per_minute"]
            for metric in key_metrics:
                dates = [h["date"] for h in historical]
                values = [h[metric.split(".")[0]][metric.split(
                    ".")[1]] if "." in metric else h[metric] for h in historical]
                baseline_mean = statistics.mean(values) if values else None

                # Store data for export
                if scenario_name not in benchmark_data:
                    benchmark_data[scenario_name] = {}
                benchmark_data[scenario_name][metric] = [
                    {"date": str(d), "value": v} for d, v in zip(dates, values)
                ]

                fig = self.create_metric_trend_plot(
                    dates, values, baseline_mean,
                    f'{metric} Trend', metric
                )
                html_parts.append(f'''
                    <div class="plot-container metric-container" 
                         data-metric="{metric}"
                         data-date="{max(dates) if dates else ''}">{fig.to_html(full_html=False)}</div>
                ''')

            html_parts.append("</div>")  # End trend view

            # Distribution view
            html_parts.append("""
                <div id="distributionContent" class="view-content" style="display: none;">
            """)

            for metric in key_metrics:
                values = [h[metric.split(".")[0]][metric.split(
                    ".")[1]] if "." in metric else h[metric] for h in historical]
                current = scenario[metric.split(".")[0]][metric.split(
                    ".")[1]] if "." in metric else scenario[metric]

                fig = self.create_metric_distribution_plot(
                    values, current, metric)
                html_parts.append(f'''
                    <div class="plot-container metric-container" 
                         data-metric="{metric}"
                         data-date="{max(dates) if dates else ''}">{fig.to_html(full_html=False)}</div>
                ''')

            html_parts.append("</div>")  # End distribution view

            # Correlation view
            html_parts.append("""
                <div id="correlationContent" class="view-content" style="display: none;">
            """)

            metrics_data = {}
            for metric in key_metrics:
                metrics_data[metric] = [h[metric.split(".")[0]][metric.split(
                    ".")[1]] if "." in metric else h[metric] for h in historical]

            fig = self.create_correlation_plot(metrics_data, key_metrics)
            html_parts.append(
                f'<div class="plot-container">{fig.to_html(full_html=False)}</div>')

            html_parts.append("</div>")  # End correlation view

        # Add benchmark data for export
        html_parts.append(f"""
                <script>
                    window.benchmarkData = {json.dumps(benchmark_data)};
                    
                    // Add click handlers for annotations
                    document.querySelectorAll('.js-plotly-plot').forEach(plot => {{
                        plot.on('plotly_click', createAnnotation);
                    }});
                </script>
            </div>
        </body>
        </html>
        """)

        return "\n".join(html_parts)

    def save_html_report(
        self,
        scenario_results: List[Dict[str, Any]],
        historical_data: Dict[str, List[Dict[str, Any]]],
        thresholds: Dict[str, Any]
    ) -> Path:
        """Generate and save the HTML report"""
        html_content = self.generate_html_report(
            scenario_results,
            historical_data,
            thresholds
        )

        output_file = self.output_dir / "benchmark_report.html"
        output_file.write_text(html_content)
        return output_file
