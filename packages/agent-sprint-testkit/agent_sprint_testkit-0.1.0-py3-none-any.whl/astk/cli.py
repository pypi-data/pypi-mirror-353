#!/usr/bin/env python3
"""
ASTK CLI - Universal AI Agent Testing
"""

import click
import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    🚀 ASTK - AgentSprint TestKit

    Universal AI agent benchmarking and testing framework.
    """
    pass


@cli.command()
@click.argument('agent_path')
@click.option('--scenarios', default=8, help='Number of test scenarios to run')
@click.option('--timeout', default=45, help='Timeout per scenario in seconds')
@click.option('--results-dir', default='astk_results', help='Results directory')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'yaml', 'markdown']))
def benchmark(agent_path: str, scenarios: int, timeout: int, results_dir: str, output_format: str):
    """
    🧪 Run intelligent benchmarks on an AI agent

    AGENT_PATH can be:
    - ./my_agent.py (Python script)
    - http://localhost:8000/chat (REST API)
    - my_module.MyAgent (Python class)
    """
    from scripts.simple_benchmark import run_benchmark_cli

    click.echo(f"🚀 ASTK Benchmark Starting...")
    click.echo(f"Agent: {agent_path}")
    click.echo(f"Scenarios: {scenarios}")
    click.echo(f"Results: {results_dir}")

    # Run the benchmark
    success = run_benchmark_cli(
        agent_path=agent_path,
        scenarios=scenarios,
        timeout=timeout,
        results_dir=results_dir,
        output_format=output_format
    )

    if success:
        click.echo("✅ Benchmark completed successfully!")
    else:
        click.echo("❌ Benchmark failed!")
        sys.exit(1)


@cli.command()
@click.argument('project_name', required=False)
@click.option('--template', default='basic', type=click.Choice(['basic', 'langchain', 'openai', 'fastapi']))
def init(project_name: Optional[str], template: str):
    """
    🏗️ Initialize a new agent project with ASTK integration
    """
    if not project_name:
        project_name = click.prompt("Project name", default="my-agent")

    project_path = Path(project_name)
    if project_path.exists():
        if not click.confirm(f"Directory {project_name} exists. Continue?"):
            return

    project_path.mkdir(exist_ok=True)

    click.echo(f"🏗️ Creating agent project: {project_name}")

    # Create basic structure
    (project_path / "agents").mkdir(exist_ok=True)
    (project_path / "tests").mkdir(exist_ok=True)
    (project_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

    # Create template files based on selection
    create_template_files(project_path, template)

    click.echo("✅ Project initialized!")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  astk benchmark agents/my_agent.py")


@cli.command()
@click.argument('results_dir', default='astk_results')
def report(results_dir: str):
    """
    📊 Generate and view benchmark reports
    """
    results_path = Path(results_dir)
    if not results_path.exists():
        click.echo(f"❌ Results directory not found: {results_dir}")
        sys.exit(1)

    # Find latest results
    json_files = list(results_path.glob("*.json"))
    if not json_files:
        click.echo(f"❌ No benchmark results found in {results_dir}")
        sys.exit(1)

    latest_result = max(json_files, key=lambda p: p.stat().st_mtime)

    click.echo(f"📊 Latest benchmark: {latest_result.name}")

    # Generate and open report
    generate_html_report(latest_result)


@cli.command()
def examples():
    """
    💡 Show example agent implementations
    """
    click.echo("🤖 Example Agent Implementations:")
    click.echo()

    examples = {
        "CLI Agent": "python my_agent.py 'query here'",
        "Python Class": "from my_agent import MyAgent; agent = MyAgent()",
        "REST API": "POST http://localhost:8000/chat {'message': 'query'}",
        "LangChain": "Use LangChain AgentExecutor pattern",
    }

    for name, example in examples.items():
        click.echo(f"📁 {name}:")
        click.echo(f"   {example}")
        click.echo()


def create_template_files(project_path: Path, template: str):
    """Create template files for different agent types"""

    # Basic agent template
    agent_template = '''#!/usr/bin/env python3
"""
Example AI Agent for ASTK Testing
"""
import sys
import asyncio

class MyAgent:
    def __init__(self):
        # Initialize your agent here
        pass
    
    async def process_query(self, query: str) -> str:
        """Process a query and return response"""
        # Your agent logic here
        return f"Agent response to: {query}"

async def main():
    agent = MyAgent()
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        response = await agent.process_query(query)
        print(f"Agent: {response}")
    else:
        print("Agent: Ready for queries!")

if __name__ == "__main__":
    asyncio.run(main())
'''

    # GitHub Actions workflow
    github_workflow = '''name: ASTK Agent Benchmark

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install ASTK
      run: |
        pip install astk
    
    - name: Run Agent Benchmarks
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        astk benchmark agents/my_agent.py --format markdown
    
    - name: Upload Results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results
        path: astk_results/
'''

    # Write files
    (project_path / "agents" / "my_agent.py").write_text(agent_template)
    (project_path / ".github" / "workflows" /
     "astk.yml").write_text(github_workflow)
    (project_path / "requirements.txt").write_text("astk>=0.1.0\n")
    (project_path / "README.md").write_text(
        f"# {project_path.name}\n\nAI Agent with ASTK Testing\n\n## Usage\n\n```bash\nastk benchmark agents/my_agent.py\n```\n")


def generate_html_report(result_file: Path):
    """Generate HTML report from JSON results"""
    import json
    import webbrowser

    with open(result_file) as f:
        data = json.load(f)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ASTK Benchmark Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #2563eb; color: white; padding: 20px; border-radius: 8px; }}
            .metric {{ background: #f3f4f6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .success {{ color: #059669; }}
            .fail {{ color: #dc2626; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 ASTK Benchmark Report</h1>
            <p>Agent: {data['agent']}</p>
            <p>Timestamp: {data['timestamp']}</p>
        </div>
        
        <div class="metric">
            <h2>📊 Summary</h2>
            <p><strong>Success Rate:</strong> <span class="success">{data['success_rate']:.1%}</span></p>
            <p><strong>Total Time:</strong> {data['total_duration_seconds']:.2f}s</p>
            <p><strong>Average Response Time:</strong> {data['average_scenario_duration']:.2f}s</p>
        </div>
        
        <h2>🧪 Scenario Details</h2>
    """

    for scenario in data['scenarios']:
        status_class = "success" if scenario['success'] else "fail"
        status_icon = "✅" if scenario['success'] else "❌"

        html_content += f"""
        <div class="metric">
            <h3>{status_icon} {scenario['scenario'].replace('_', ' ').title()}</h3>
            <p><strong>Query:</strong> {scenario['query']}</p>
            <p><strong>Duration:</strong> {scenario['duration_seconds']:.2f}s</p>
            <p class="{status_class}"><strong>Status:</strong> {"PASS" if scenario['success'] else "FAIL"}</p>
        </div>
        """

    html_content += "</body></html>"

    # Save and open report
    report_file = result_file.parent / "report.html"
    report_file.write_text(html_content)

    click.echo(f"📊 Report generated: {report_file}")
    webbrowser.open(f"file://{report_file.absolute()}")


if __name__ == "__main__":
    cli()
