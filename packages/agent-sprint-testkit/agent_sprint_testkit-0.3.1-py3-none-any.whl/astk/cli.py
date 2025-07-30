#!/usr/bin/env python3
"""
ASTK CLI - Universal AI Agent Testing
"""

import click
import sys
import os
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional, List
import webbrowser


@click.group()
@click.version_option(version="0.3.0")
def cli():
    """
    🚀 ASTK - AgentSprint TestKit v0.3.0

    Professional AI agent evaluation and testing framework with multi-tier assessment capabilities.

    📊 AVAILABLE TESTING TIERS:

    🟢 TIER 1 - BASIC TESTING (Quick Development)
    • astk benchmark <agent>              - 12 intelligent scenarios (100% pass rate shown above)
    • astk examples                       - Example agent implementations
    • Fast feedback for development iterations

    🟡 TIER 2 - PROFESSIONAL EVALUATION (Production Ready)  
    • astk evals create <agent>           - OpenAI Evals integration
    • astk evals run <eval_id>            - Professional grading system
    • Industry-standard evaluation with detailed reports

    🔴 TIER 3 - RIGOROUS MULTI-LAYER (Expert Assessment)
    • astk rigorous run <agent>           - 9 expert-level scenarios
    • Multiple OpenAI evaluators per scenario (GPT-4, O1-Preview)
    • PhD-level challenges with 7.0+ pass thresholds
    • Cost: ~$7-15 per full evaluation

    💡 QUICK START EXAMPLES:
      # Development testing (free, fast)
      python -m astk.cli benchmark my_agent.py

      # Professional evaluation (~$1-3)
      python -m astk.cli evals create my_agent.py --eval-type code_qa

      # Rigorous assessment (~$7-15) 
      python -m astk.cli rigorous run my_agent.py --max-cost 10.0

    📚 DOCUMENTATION:
      README.md                    - Complete feature overview
      RELIABLE_CLI_USAGE.md        - Cross-platform usage guide  
      HOW_TO_RUN_RIGOROUS_EVALUATION.md - Expert evaluation guide

    🔧 SETUP COMMANDS:
      astk init <project>          - Initialize new agent project
      astk report <results_dir>    - Generate HTML reports

    For reliable usage across all environments, always use:
    python -m astk.cli <command>
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
    💡 Show testing examples and comprehensive tier guide
    """
    click.echo("🚀 ASTK Testing Tiers & Examples")
    click.echo("=" * 50)
    click.echo()

    # Tier 1: Basic Testing
    click.echo("🟢 TIER 1: BASIC TESTING (Development)")
    click.echo("   Purpose: Quick feedback during development")
    click.echo("   Cost: FREE")
    click.echo("   Time: ~2-3 minutes")
    click.echo("   Pass Rate: 80-100% (designed for success)")
    click.echo()
    click.echo("   Commands:")
    click.echo("   python -m astk.cli benchmark my_agent.py")
    click.echo("   python -m astk.cli benchmark my_agent.py --scenarios 5")
    click.echo()

    # Tier 2: Professional Evaluation
    click.echo("🟡 TIER 2: PROFESSIONAL EVALUATION (Production)")
    click.echo("   Purpose: Industry-standard assessment")
    click.echo("   Cost: $1-5 per evaluation")
    click.echo("   Time: ~5-10 minutes")
    click.echo("   Pass Rate: 60-80% (professional standards)")
    click.echo()
    click.echo("   Commands:")
    click.echo(
        "   python -m astk.cli evals create my_agent.py --eval-type code_qa")
    click.echo(
        "   python -m astk.cli evals create my_agent.py --eval-type research")
    click.echo("   python -m astk.cli evals run <eval_id>")
    click.echo()

    # Tier 3: Rigorous Multi-Layer
    click.echo("🔴 TIER 3: RIGOROUS MULTI-LAYER (Expert)")
    click.echo("   Purpose: Comprehensive expert-level assessment")
    click.echo("   Cost: $7-15 per evaluation")
    click.echo("   Time: ~10-20 minutes")
    click.echo("   Pass Rate: 10-30% (PhD-level challenges)")
    click.echo()
    click.echo("   Commands:")
    click.echo("   # Basic rigorous test")
    click.echo("   python -m astk.cli rigorous run my_agent.py --max-cost 10.0")
    click.echo()
    click.echo("   # Development-friendly (lower cost)")
    click.echo(
        "   python -m astk.cli rigorous run my_agent.py --max-cost 3.0 --fail-fast")
    click.echo()
    click.echo("   # Full assessment (parallel)")
    click.echo(
        "   python -m astk.cli rigorous run my_agent.py --parallel --max-cost 20.0")
    click.echo()

    click.echo("🎯 RECOMMENDATION BY USE CASE:")
    click.echo()

    use_cases = {
        "Daily Development": "🟢 Tier 1 - astk benchmark (free, fast feedback)",
        "Pre-Production": "🟡 Tier 2 - astk evals (professional validation)",
        "Research/Competition": "🔴 Tier 3 - astk rigorous (expert assessment)",
        "CI/CD Pipeline": "🟢 Tier 1 + 🟡 Tier 2 (automated quality gates)",
        "Academic Research": "🔴 Tier 3 (rigorous scientific evaluation)",
        "Commercial Deployment": "🟡 Tier 2 → 🔴 Tier 3 (staged validation)"
    }

    for use_case, recommendation in use_cases.items():
        click.echo(f"   {use_case}: {recommendation}")

    click.echo()
    click.echo("🤖 AGENT IMPLEMENTATION EXAMPLES:")
    click.echo()

    examples = {
        "CLI Agent": "python my_agent.py 'query here'",
        "Python Class": "from my_agent import MyAgent; agent = MyAgent()",
        "REST API": "POST http://localhost:8000/chat {'message': 'query'}",
        "LangChain": "Use LangChain AgentExecutor pattern",
        "OpenAI Function": "Use OpenAI function calling format"
    }

    for name, example in examples.items():
        click.echo(f"   📁 {name}:")
        click.echo(f"      {example}")
        click.echo()

    click.echo("📚 DOCUMENTATION:")
    click.echo("   README.md - Complete overview and setup")
    click.echo("   RELIABLE_CLI_USAGE.md - Cross-platform usage guide")
    click.echo("   HOW_TO_RUN_RIGOROUS_EVALUATION.md - Expert evaluation guide")
    click.echo()
    click.echo(
        "💡 TIP: Start with Tier 1, then progress to higher tiers as your agent improves!")


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
        # Check for OpenAI API key first
        if not os.getenv("OPENAI_API_KEY"):
            click.echo("❌ OpenAI API key required for evaluation creation")
            click.echo("💡 Set your API key:")
            click.echo("   export OPENAI_API_KEY='your-api-key-here'")
            click.echo(
                "   # Get your key from: https://platform.openai.com/api-keys")
            sys.exit(1)

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
        click.echo("💡 Ensure OPENAI_API_KEY is set and valid")
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
        # Check for OpenAI API key first
        if not os.getenv("OPENAI_API_KEY"):
            click.echo("❌ OpenAI API key required for running evaluations")
            click.echo("💡 Set your API key:")
            click.echo("   export OPENAI_API_KEY='your-api-key-here'")
            click.echo(
                "   # Get your key from: https://platform.openai.com/api-keys")
            sys.exit(1)

        adapter = OpenAIEvalsAdapter()
        run_id = adapter.evaluate_from_logs(eval_id, days_back=7)

        click.echo(f"✅ Evaluation started!")
        click.echo(f"🔗 Run ID: {run_id}")
        click.echo(
            f"📊 View results at: https://platform.openai.com/evals/runs/{run_id}")

    except Exception as e:
        click.echo(f"❌ Failed to run evaluation: {e}")
        click.echo("💡 Ensure OPENAI_API_KEY is set and valid")
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
        # Check for OpenAI API key first
        if not os.getenv("OPENAI_API_KEY"):
            click.echo("❌ OpenAI API key required for model comparison")
            click.echo("💡 Set your API key:")
            click.echo("   export OPENAI_API_KEY='your-api-key-here'")
            click.echo(
                "   # Get your key from: https://platform.openai.com/api-keys")
            sys.exit(1)

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
        click.echo("💡 Ensure OPENAI_API_KEY is set and valid")
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
        python -m astk.cli benchmark agents/my_agent.py --format markdown
    
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
        f"# {project_path.name}\n\nAI Agent with ASTK Testing\n\n## Usage\n\n```bash\npython -m astk.cli benchmark agents/my_agent.py\n```\n")


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


@cli.group()
def rigorous():
    """🔬 Rigorous multi-layer evaluation scenarios with OpenAI grading"""
    pass


@rigorous.command()
@click.argument('agent_path')
@click.option('--scenarios', default='examples/benchmarks/scenarios/rigorous_multilayer_scenarios.yaml',
              help='Path to rigorous scenarios YAML file')
@click.option('--evaluators', multiple=True,
              default=['gpt-4', 'o1-preview'],
              help='OpenAI models to use as evaluators')
@click.option('--parallel', is_flag=True, default=False,
              help='Run scenarios in parallel (faster but more expensive)')
@click.option('--max-cost', type=float, default=10.0,
              help='Maximum total cost in USD for all evaluations')
@click.option('--output-format', type=click.Choice(['json', 'yaml', 'detailed']),
              default='detailed', help='Output format for results')
@click.option('--save-results', is_flag=True, default=True,
              help='Save detailed results to file')
@click.option('--fail-fast', is_flag=True, default=False,
              help='Stop on first scenario failure')
@click.option('--retry-failures', type=int, default=1,
              help='Number of retry attempts for failed evaluations')
def run(agent_path: str, scenarios: str, evaluators: tuple, parallel: bool,
        max_cost: float, output_format: str, save_results: bool,
        fail_fast: bool, retry_failures: int):
    """
    🚀 Run rigorous multi-layer evaluation scenarios

    This command runs sophisticated evaluation scenarios that use multiple layers
    of OpenAI evaluation for comprehensive agent assessment.

    Example:
        astk rigorous run my_agent.py --evaluators gpt-4 o1-preview --max-cost 15.0
    """
    import yaml
    import asyncio
    from datetime import datetime
    from pathlib import Path

    try:
        from .evals_integration import OpenAIEvalsAdapter, MultiLayerEvaluationResult
        from .schema import ScenarioConfig, BenchmarkSuite, TestSession, AgentConfig, EvaluationResult
    except ImportError as e:
        click.echo(f"❌ Multi-layer evaluation not available: {e}")
        click.echo("💡 Install with: pip install openai>=1.50.0")
        sys.exit(1)

    click.echo("🔬 ASTK Rigorous Multi-Layer Evaluation")
    click.echo("=" * 50)
    click.echo(f"🎯 Agent: {agent_path}")
    click.echo(f"📋 Scenarios: {scenarios}")
    click.echo(f"🤖 Evaluators: {', '.join(evaluators)}")
    click.echo(f"💰 Max Cost: ${max_cost:.2f}")
    click.echo(f"⚡ Parallel: {'Yes' if parallel else 'No'}")
    click.echo()

    # Load scenarios
    try:
        with open(scenarios, 'r') as f:
            scenarios_data = yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"❌ Scenarios file not found: {scenarios}")
        sys.exit(1)
    except yaml.YAMLError as e:
        click.echo(f"❌ Invalid YAML in scenarios file: {e}")
        sys.exit(1)

    # Parse scenarios
    try:
        scenario_configs = []
        for scenario_data in scenarios_data.get('scenarios', []):
            # Convert YAML structure to ScenarioConfig
            scenario_config = _parse_yaml_scenario(scenario_data)
            scenario_configs.append(scenario_config)

        if not scenario_configs:
            click.echo("❌ No valid scenarios found in file")
            sys.exit(1)

        click.echo(f"✅ Loaded {len(scenario_configs)} rigorous scenarios")

        # Display scenario summary
        difficulty_counts = {}
        category_counts = {}
        total_estimated_cost = 0.0

        for config in scenario_configs:
            difficulty = getattr(config, 'difficulty', 'unknown')
            category = getattr(config, 'category', 'unknown')

            difficulty_counts[difficulty] = difficulty_counts.get(
                difficulty, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1

            if hasattr(config, 'budgets') and config.budgets and config.budgets.cost_usd:
                total_estimated_cost += config.budgets.cost_usd

        click.echo(f"📊 Difficulty distribution: {dict(difficulty_counts)}")
        click.echo(f"🏷️  Category distribution: {dict(category_counts)}")
        click.echo(f"💸 Estimated total cost: ${total_estimated_cost:.2f}")

        if total_estimated_cost > max_cost:
            click.echo(f"⚠️  Estimated cost exceeds maximum (${max_cost:.2f})")
            if not click.confirm("Continue anyway?"):
                sys.exit(0)

        click.echo()

    except Exception as e:
        click.echo(f"❌ Error parsing scenarios: {e}")
        sys.exit(1)

    # Initialize evaluation system
    try:
        # Check for OpenAI API key first
        if not os.getenv("OPENAI_API_KEY"):
            click.echo("❌ OpenAI API key required for rigorous evaluation")
            click.echo("💡 Set your API key:")
            click.echo("   export OPENAI_API_KEY='your-api-key-here'")
            click.echo(
                "   # Get your key from: https://platform.openai.com/api-keys")
            sys.exit(1)

        adapter = OpenAIEvalsAdapter()
        click.echo("✅ OpenAI Evals adapter initialized")
    except Exception as e:
        click.echo(f"❌ Failed to initialize OpenAI Evals: {e}")
        click.echo("💡 Ensure OPENAI_API_KEY is set and valid")
        sys.exit(1)

    # Run evaluation
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = datetime.now()

    click.echo("🚀 Starting rigorous evaluation...")
    click.echo()

    results = []
    total_cost = 0.0
    scenarios_passed = 0

    try:
        for i, scenario_config in enumerate(scenario_configs, 1):
            scenario_name = getattr(scenario_config, 'name', f'scenario_{i}')
            click.echo(
                f"[{i}/{len(scenario_configs)}] 🧪 Testing: {scenario_name}")

            scenario_start = datetime.now()

            try:
                # Run the agent scenario
                agent_response = _run_agent_scenario(
                    agent_path, scenario_config)

                # Perform multi-layer evaluation
                evaluation_result = adapter.evaluate_response_multilayer(
                    response=agent_response,
                    scenario_config=scenario_config,
                    context={"evaluators": evaluators}
                )

                scenario_end = datetime.now()
                execution_time = int(
                    (scenario_end - scenario_start).total_seconds() * 1000)

                # Calculate cost (estimate based on tokens and evaluator calls)
                scenario_cost = _estimate_scenario_cost(
                    evaluation_result, scenario_config)
                total_cost += scenario_cost

                # Create detailed result
                result = EvaluationResult(
                    scenario_name=scenario_name,
                    passed=evaluation_result.passed,
                    overall_score=evaluation_result.overall_score,
                    layer_results=evaluation_result.layer_results,
                    execution_time_ms=execution_time,
                    cost_usd=scenario_cost,
                    tokens_used=len(agent_response) // 4,  # Rough estimate
                    timestamp=scenario_end.isoformat()
                )

                # Extract feedback from evaluation
                for layer_name, layer_data in evaluation_result.layer_results.items():
                    feedback = layer_data.get('feedback', '')
                    if isinstance(feedback, str) and feedback.startswith('{'):
                        try:
                            feedback_data = json.loads(feedback)
                            result.strengths.extend(
                                feedback_data.get('strengths', []))
                            result.weaknesses.extend(
                                feedback_data.get('weaknesses', []))
                            result.recommendations.extend(
                                feedback_data.get('recommendations', []))
                        except:
                            pass

                results.append(result)

                if evaluation_result.passed:
                    scenarios_passed += 1
                    status = "✅ PASS"
                    score_color = click.style(
                        f"{evaluation_result.overall_score:.1f}/10", fg='green')
                else:
                    if evaluation_result.overall_score > 7:
                        status = "❌ FAIL (likely to a failure in one of the models' evaluations)"
                        score_color = click.style(
                            f"{evaluation_result.overall_score:.1f}/10", fg='red')
                    else:
                        status = "❌ FAIL"
                        score_color = click.style(
                            f"{evaluation_result.overall_score:.1f}/10", fg='red')

                click.echo(
                    f"   {status} Score: {score_color} Cost: ${scenario_cost:.3f} Time: {execution_time}ms")

                # Show layer breakdown
                for layer_name, layer_data in evaluation_result.layer_results.items():
                    layer_score = layer_data.get('score', 0)
                    evaluator = layer_data.get('evaluator', 'unknown')
                    layer_color = click.style(f"{layer_score:.1f}",
                                              fg='green' if layer_score >= 7 else 'yellow' if layer_score >= 5 else 'red')
                    click.echo(
                        f"     └ {layer_name} ({evaluator}): {layer_color}")

                if total_cost > max_cost:
                    click.echo(
                        f"💰 Cost limit exceeded (${total_cost:.2f} > ${max_cost:.2f})")
                    break

                if fail_fast and not evaluation_result.passed:
                    click.echo(
                        "⏹️  Fail-fast enabled, stopping on first failure")
                    break

            except Exception as e:
                click.echo(f"   ❌ Error: {str(e)}")
                if retry_failures > 0:
                    click.echo(
                        f"   🔄 Retrying ({retry_failures} attempts left)...")
                    retry_failures -= 1
                    continue
                else:
                    click.echo(
                        f"   ⏭️  Skipping scenario due to repeated failures")

            click.echo()

    except KeyboardInterrupt:
        click.echo("\n⏹️  Evaluation interrupted by user")

    # Generate summary
    end_time = datetime.now()
    total_duration = int((end_time - start_time).total_seconds() * 1000)
    pass_rate = scenarios_passed / len(results) if results else 0

    click.echo("🏁 EVALUATION COMPLETE")
    click.echo("=" * 50)
    click.echo(
        f"📊 Results: {scenarios_passed}/{len(results)} passed ({pass_rate:.1%})")
    click.echo(f"💰 Total Cost: ${total_cost:.2f}")
    click.echo(f"⏱️  Total Time: {total_duration/1000:.1f}s")

    if results:
        avg_score = sum(r.overall_score for r in results) / len(results)
        score_color = click.style(f"{avg_score:.1f}/10",
                                  fg='green' if avg_score >= 7 else 'yellow' if avg_score >= 5 else 'red')
        click.echo(f"🎯 Average Score: {score_color}")

        # Category and difficulty breakdown
        _display_performance_breakdown(results, scenario_configs)

    # Save results if requested
    if save_results and results:
        results_file = f"rigorous_evaluation_{session_id}.json"

        # Create comprehensive session data
        session_data = {
            "session_id": session_id,
            "agent_path": agent_path,
            "scenarios_file": scenarios,
            "evaluators": list(evaluators),
            "settings": {
                "parallel": parallel,
                "max_cost": max_cost,
                "fail_fast": fail_fast,
                "retry_failures": retry_failures
            },
            "summary": {
                "total_scenarios": len(scenario_configs),
                "scenarios_run": len(results),
                "scenarios_passed": scenarios_passed,
                "pass_rate": pass_rate,
                "average_score": avg_score if results else 0,
                "total_cost_usd": total_cost,
                "total_duration_ms": total_duration
            },
            "results": [result.model_dump() for result in results],
            "timestamp": end_time.isoformat()
        }

        if output_format == 'json':
            with open(results_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        elif output_format == 'yaml':
            results_file = results_file.replace('.json', '.yaml')
            with open(results_file, 'w') as f:
                yaml.dump(session_data, f, default_flow_style=False)
        else:  # detailed
            _save_detailed_results(
                session_data, results_file.replace('.json', '_detailed.md'))

        click.echo(f"💾 Results saved to: {results_file}")

    # Exit with appropriate code
    if pass_rate >= 0.7:  # 70% pass rate threshold
        click.echo("🎉 Evaluation PASSED!")
        sys.exit(0)
    else:
        click.echo("⚠️  Evaluation FAILED - Low pass rate")
        sys.exit(1)


def _parse_yaml_scenario(scenario_data: dict) -> 'ScenarioConfig':
    """Parse YAML scenario data into ScenarioConfig"""
    from .schema import ScenarioConfig, PersonaConfig, SuccessCriteria, BudgetConfig, ChaosConfig, OpenAIEvaluationConfig

    # Parse persona
    persona_data = scenario_data.get('persona', {})
    persona = PersonaConfig(
        archetype=persona_data.get('archetype', 'general'),
        temperature=persona_data.get('temperature', 0.7),
        traits=persona_data.get('traits', [])
    )

    # Parse success criteria
    success_data = scenario_data.get('success', {})

    # Parse OpenAI evaluations
    openai_evals = []
    for eval_data in success_data.get('openai_evaluations', []):
        openai_eval = OpenAIEvaluationConfig(
            evaluator=eval_data.get('evaluator', 'gpt-4'),
            prompt=eval_data.get('prompt', ''),
            pass_threshold=eval_data.get('pass_threshold', 7.0),
            weight=eval_data.get('weight', 1.0),
            evaluation_type=eval_data.get('evaluation_type', 'general')
        )
        openai_evals.append(openai_eval)

    success = SuccessCriteria(
        regex=success_data.get('regex'),
        semantic_score=success_data.get('semantic_score'),
        task_specific=success_data.get('task_specific'),
        openai_evaluations=openai_evals,
        require_all_evaluations_pass=success_data.get(
            'require_all_evaluations_pass', True),
        overall_pass_threshold=success_data.get('overall_pass_threshold', 7.0)
    )

    # Parse budgets
    budgets = None
    if 'budgets' in scenario_data:
        budget_data = scenario_data['budgets']
        budgets = BudgetConfig(
            latency_ms=budget_data.get('latency_ms'),
            cost_usd=budget_data.get('cost_usd'),
            tokens=budget_data.get('tokens'),
            evaluation_cost_usd=budget_data.get('evaluation_cost_usd'),
            retry_budget=budget_data.get('retry_budget', 3)
        )

    # Parse chaos
    chaos = None
    if 'chaos' in scenario_data:
        chaos_data = scenario_data['chaos']
        chaos = ChaosConfig(
            drop_tool=chaos_data.get('drop_tool', []),
            inject_latency=chaos_data.get('inject_latency', []),
            malform_messages=chaos_data.get('malform_messages', False),
            adversarial_prompts=chaos_data.get('adversarial_prompts', False),
            memory_pressure=chaos_data.get('memory_pressure', False),
            network_instability=chaos_data.get('network_instability', False)
        )

    return ScenarioConfig(
        name=scenario_data.get('name'),
        task=scenario_data.get('task', 'unknown'),
        description=scenario_data.get('description'),
        difficulty=scenario_data.get('difficulty', 'intermediate'),
        category=scenario_data.get('category', 'general'),
        persona=persona,
        protocol=scenario_data.get('protocol', 'A2A'),
        success=success,
        input_prompt=scenario_data.get('input_prompt'),
        budgets=budgets,
        chaos=chaos
    )


def _run_agent_scenario(agent_path: str, scenario_config: 'ScenarioConfig') -> str:
    """Run agent with scenario input and return response"""
    import subprocess

    input_prompt = getattr(scenario_config, 'input_prompt',
                           '') or f"Execute task: {scenario_config.task}"

    try:
        result = subprocess.run([
            sys.executable, agent_path, input_prompt
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(
                f"Agent failed with return code {result.returncode}: {result.stderr}")

    except subprocess.TimeoutExpired:
        raise Exception("Agent execution timed out after 60 seconds")
    except Exception as e:
        raise Exception(f"Agent execution failed: {str(e)}")


def _estimate_scenario_cost(evaluation_result: 'MultiLayerEvaluationResult', scenario_config: 'ScenarioConfig') -> float:
    """Estimate the cost of running a scenario with multi-layer evaluation"""

    # Base cost for scenario execution
    base_cost = 0.001

    # Cost per OpenAI evaluation (rough estimate)
    # GPT-4: ~$0.03/1K tokens, O1-preview: ~$0.15/1K tokens
    eval_costs = {
        'gpt-4': 0.005,
        'gpt-4-turbo': 0.004,
        'o1-preview': 0.020,
        'o1-mini': 0.010
    }

    total_cost = base_cost

    for layer_name, layer_data in evaluation_result.layer_results.items():
        evaluator = layer_data.get('evaluator', 'gpt-4')
        if evaluator in eval_costs:
            total_cost += eval_costs[evaluator]
        else:
            total_cost += 0.005  # Default cost

    return total_cost


def _display_performance_breakdown(results: List['EvaluationResult'], scenario_configs: List['ScenarioConfig']):
    """Display detailed performance breakdown by category and difficulty"""

    # Category performance
    category_performance = {}
    difficulty_performance = {}

    for i, result in enumerate(results):
        if i < len(scenario_configs):
            config = scenario_configs[i]
            category = getattr(config, 'category', 'unknown')
            difficulty = getattr(config, 'difficulty', 'unknown')

            if category not in category_performance:
                category_performance[category] = []
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = []

            category_performance[category].append(result.overall_score)
            difficulty_performance[difficulty].append(result.overall_score)

    if category_performance:
        click.echo("\n📂 Performance by Category:")
        for category, scores in category_performance.items():
            avg_score = sum(scores) / len(scores)
            pass_rate = sum(1 for s in scores if s >= 7) / len(scores)
            score_color = click.style(f"{avg_score:.1f}",
                                      fg='green' if avg_score >= 7 else 'yellow' if avg_score >= 5 else 'red')
            click.echo(
                f"   {category}: {score_color}/10 ({pass_rate:.0%} pass rate)")

    if difficulty_performance:
        click.echo("\n🎓 Performance by Difficulty:")
        for difficulty, scores in difficulty_performance.items():
            avg_score = sum(scores) / len(scores)
            pass_rate = sum(1 for s in scores if s >= 7) / len(scores)
            score_color = click.style(f"{avg_score:.1f}",
                                      fg='green' if avg_score >= 7 else 'yellow' if avg_score >= 5 else 'red')
            click.echo(
                f"   {difficulty}: {score_color}/10 ({pass_rate:.0%} pass rate)")


def _save_detailed_results(session_data: dict, filename: str):
    """Save detailed markdown report of the evaluation results"""

    with open(filename, 'w') as f:
        f.write(f"# ASTK Rigorous Multi-Layer Evaluation Report\n\n")
        f.write(f"**Session ID:** {session_data['session_id']}\n")
        f.write(f"**Agent:** {session_data['agent_path']}\n")
        f.write(f"**Timestamp:** {session_data['timestamp']}\n\n")

        # Summary
        summary = session_data['summary']
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Scenarios:** {summary['total_scenarios']}\n")
        f.write(f"- **Scenarios Run:** {summary['scenarios_run']}\n")
        f.write(f"- **Pass Rate:** {summary['pass_rate']:.1%}\n")
        f.write(f"- **Average Score:** {summary['average_score']:.1f}/10\n")
        f.write(f"- **Total Cost:** ${summary['total_cost_usd']:.2f}\n")
        f.write(
            f"- **Total Duration:** {summary['total_duration_ms']/1000:.1f}s\n\n")

        # Detailed results
        f.write(f"## Detailed Results\n\n")

        for result_data in session_data['results']:
            f.write(f"### {result_data['scenario_name']}\n\n")

            status = "✅ PASSED" if result_data['passed'] else "❌ FAILED"
            f.write(f"**Status:** {status}\n")
            f.write(
                f"**Overall Score:** {result_data['overall_score']:.1f}/10\n")
            f.write(
                f"**Execution Time:** {result_data['execution_time_ms']}ms\n")
            f.write(f"**Cost:** ${result_data['cost_usd']:.3f}\n\n")

            # Layer results
            if result_data['layer_results']:
                f.write(f"**Evaluation Layers:**\n")
                for layer_name, layer_data in result_data['layer_results'].items():
                    score = layer_data.get('score', 0)
                    evaluator = layer_data.get('evaluator', 'unknown')
                    f.write(f"- {layer_name} ({evaluator}): {score:.1f}/10\n")
                f.write("\n")

            # Feedback
            if result_data.get('strengths'):
                f.write(f"**Strengths:**\n")
                for strength in result_data['strengths']:
                    f.write(f"- {strength}\n")
                f.write("\n")

            if result_data.get('weaknesses'):
                f.write(f"**Areas for Improvement:**\n")
                for weakness in result_data['weaknesses']:
                    f.write(f"- {weakness}\n")
                f.write("\n")

            if result_data.get('recommendations'):
                f.write(f"**Recommendations:**\n")
                for rec in result_data['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")

            f.write("---\n\n")


if __name__ == "__main__":
    cli()
