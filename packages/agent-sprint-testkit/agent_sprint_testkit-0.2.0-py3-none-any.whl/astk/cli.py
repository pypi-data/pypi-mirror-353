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
import webbrowser


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """
    🚀 ASTK - AgentSprint TestKit

    Professional AI agent evaluation and testing framework with OpenAI Evals integration.

    For reliable usage across all environments, use:
    python -m astk.cli <command>

    See RELIABLE_CLI_USAGE.md for complete guidance.
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
    import subprocess
    from pathlib import Path

    click.echo(f"🚀 ASTK Benchmark Starting...")
    click.echo(f"Agent: {agent_path}")
    click.echo(f"Results: {results_dir}")

    # Run the benchmark script directly
    script_path = Path(__file__).parent.parent / \
        "scripts" / "simple_benchmark.py"

    try:
        # Pass arguments in the correct order: agent_path --results-dir results_dir
        result = subprocess.run([
            sys.executable, str(
                script_path), agent_path, "--results-dir", results_dir
        ], check=True)

        click.echo("✅ Benchmark completed successfully!")

    except subprocess.CalledProcessError:
        click.echo("❌ Benchmark failed!")
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ Benchmark script not found!")
        click.echo("💡 Try running directly: python scripts/simple_benchmark.py")
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
    click.echo(f"  python -m astk.cli benchmark agents/my_agent.py")


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


# NEW: OpenAI Evals Integration Commands
@cli.group()
def evals():
    """
    🎯 OpenAI Evals API integration commands (Beta)

    Professional-grade agent evaluation using OpenAI's Evals infrastructure.
    Requires: pip install openai>=1.50.0
    """
    pass


@evals.command()
@click.argument('agent_path')
@click.option('--grader', default='gpt-4', type=click.Choice(['gpt-4', 'gpt-4-turbo', 'o3', 'o3-mini']))
@click.option('--eval-type', default='general', type=click.Choice(['general', 'code_qa', 'customer_service', 'research']))
@click.option('--scenarios', default=10, help='Number of test scenarios')
@click.option('--pass-threshold', default=6.0, type=float, help='Minimum score to pass (1-10)')
def create(agent_path: str, grader: str, eval_type: str, scenarios: int, pass_threshold: float):
    """
    🎯 Create a new OpenAI Eval for your agent

    This creates a professional evaluation using OpenAI's infrastructure.
    """
    try:
        from .evals_integration import OpenAIEvalsAdapter
        from .schema import ScenarioConfig, PersonaConfig, SuccessCriteria
    except ImportError as e:
        click.echo(f"❌ OpenAI Evals integration not available: {e}")
        click.echo("💡 Install with: pip install openai>=1.50.0")
        sys.exit(1)

    click.echo(f"🎯 Creating OpenAI Eval for: {agent_path}")
    click.echo(f"📊 Grader: {grader}")
    click.echo(f"🔍 Type: {eval_type}")

    try:
        adapter = OpenAIEvalsAdapter()

        # Create sample scenarios based on eval type
        test_scenarios = generate_test_scenarios(eval_type, scenarios)

        eval_id = adapter.create_eval_from_scenarios(
            scenarios=test_scenarios,
            eval_name=f"ASTK-{eval_type}-{agent_path}",
            grader_model=grader
        )

        click.echo(f"✅ Eval created successfully!")
        click.echo(f"📋 Eval ID: {eval_id}")
        click.echo(f"🚀 Run with: python -m astk.cli evals run {eval_id}")

    except Exception as e:
        click.echo(f"❌ Failed to create eval: {e}")
        sys.exit(1)


@evals.command()
@click.argument('eval_id')
@click.option('--data-limit', default=50, help='Number of samples to evaluate')
def run(eval_id: str, data_limit: int):
    """
    🚀 Run an evaluation using logged responses

    This evaluates your agent based on recent logs.
    """
    try:
        from .evals_integration import OpenAIEvalsAdapter
    except ImportError as e:
        click.echo(f"❌ OpenAI Evals integration not available: {e}")
        sys.exit(1)

    click.echo(f"🚀 Running evaluation: {eval_id}")
    click.echo(f"📊 Samples: {data_limit}")

    try:
        adapter = OpenAIEvalsAdapter()
        run_id = adapter.evaluate_from_logs(eval_id, days_back=7)

        click.echo(f"✅ Evaluation started!")
        click.echo(f"🔗 Run ID: {run_id}")
        click.echo(
            f"📊 View results at: https://platform.openai.com/evals/runs/{run_id}")

    except Exception as e:
        click.echo(f"❌ Failed to run evaluation: {e}")
        sys.exit(1)


@evals.command()
@click.argument('eval_id')
@click.argument('baseline_model')
@click.argument('test_model')
@click.option('--data-limit', default=30, help='Number of samples to compare')
def compare(eval_id: str, baseline_model: str, test_model: str, data_limit: int):
    """
    ⚖️ Compare two models using the same evaluation

    This runs A/B testing between two different models.
    """
    try:
        from .evals_integration import OpenAIEvalsAdapter
    except ImportError as e:
        click.echo(f"❌ OpenAI Evals integration not available: {e}")
        sys.exit(1)

    click.echo(f"⚖️ Comparing models:")
    click.echo(f"  📊 Baseline: {baseline_model}")
    click.echo(f"  🆚 Test: {test_model}")
    click.echo(f"  📋 Eval: {eval_id}")

    try:
        adapter = OpenAIEvalsAdapter()
        results = adapter.run_comparative_evaluation(
            eval_id=eval_id,
            baseline_model=baseline_model,
            test_model=test_model,
            data_limit=data_limit
        )

        click.echo(f"✅ Comparison started!")
        click.echo(f"🔗 View results: {results['comparison_url']}")

    except Exception as e:
        click.echo(f"❌ Failed to run comparison: {e}")
        sys.exit(1)


def generate_test_scenarios(eval_type: str, count: int):
    """Generate test scenarios based on evaluation type"""
    from .schema import ScenarioConfig, PersonaConfig, SuccessCriteria

    # Sample scenarios for different types
    scenario_templates = {
        "code_qa": [
            {"task": "explain_function", "query": "What does this function do?"},
            {"task": "debug_code", "query": "Find the bug in this code"},
            {"task": "optimize_code", "query": "How can this code be improved?"},
        ],
        "customer_service": [
            {"task": "product_inquiry", "query": "Tell me about your product features"},
            {"task": "billing_issue", "query": "I have a question about my bill"},
            {"task": "technical_support", "query": "I'm having trouble with the app"},
        ],
        "research": [
            {"task": "market_analysis", "query": "Analyze the current market trends"},
            {"task": "competitive_research",
                "query": "Who are our main competitors?"},
            {"task": "data_synthesis", "query": "Summarize these research findings"},
        ],
        "general": [
            {"task": "general_query", "query": "Help me understand this topic"},
            {"task": "problem_solving", "query": "How would you approach this problem?"},
            {"task": "explanation", "query": "Explain this concept clearly"},
        ]
    }

    templates = scenario_templates.get(
        eval_type, scenario_templates["general"])
    scenarios = []

    for i in range(count):
        template = templates[i % len(templates)]
        scenarios.append(ScenarioConfig(
            task=template["task"],
            persona=PersonaConfig(archetype="professional_user"),
            protocol="A2A",
            success=SuccessCriteria(semantic_score=0.7)
        ))

    return scenarios


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
        pip install agent-sprint-testkit
    
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


def main_wrapper():
    """Wrapper to call the sophisticated benchmark script"""
    import subprocess
    import sys
    from pathlib import Path

    # Check if we should show help
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        print("🚀 ASTK - AgentSprint TestKit")
        print("Sophisticated AI Agent Benchmarking")
        print()
        print("Usage:")
        print("  python -m astk.cli benchmark <agent_path>  - Run sophisticated benchmark")
        print("  python -m astk.cli examples               - Show usage examples")
        print("  python -m astk.cli init <project>         - Initialize new project")
        print()
        print("Examples:")
        print("  python -m astk.cli benchmark examples/agents/file_qa_agent.py")
        print("  python -m astk.cli benchmark my_agent.py --results-dir results/")
        print()
        print("Features:")
        print("  📊 12 sophisticated scenarios across multiple categories")
        print("  🧠 Advanced reasoning and problem-solving tests")
        print("  🎯 Complexity scoring with difficulty weighting")
        print("  📈 Category performance breakdown")
        print("  🌟 AI capability assessment")
        print()
        return

    # Find the script path relative to the package
    script_path = Path(__file__).parent.parent / \
        "scripts" / "simple_benchmark.py"

    # Call the sophisticated benchmark script
    try:
        subprocess.run([sys.executable, str(script_path)] +
                       sys.argv[1:], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


def benchmark_wrapper():
    """Wrapper for astk-benchmark command"""
    main_wrapper()


def run_wrapper():
    """Wrapper to call the simple run script"""
    import subprocess
    import sys
    from pathlib import Path

    # Find the script path relative to the package
    script_path = Path(__file__).parent.parent / "scripts" / "simple_run.py"

    # Call the simple run script
    try:
        subprocess.run([sys.executable, str(script_path)] +
                       sys.argv[1:], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    cli()
