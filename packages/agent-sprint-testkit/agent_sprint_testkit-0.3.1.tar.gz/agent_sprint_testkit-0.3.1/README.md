# AgentSprint TestKit (ASTK) 🚀

> **Professional AI agent evaluation and testing framework with multi-tier assessment capabilities**

ASTK is a comprehensive testing framework for AI agents that evaluates performance, intelligence, and capabilities through diverse scenarios. Test your agents against real-world tasks ranging from basic functionality to expert-level multi-layer evaluation using OpenAI's professional grading infrastructure.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![PyPI Version](https://img.shields.io/pypi/v/agent-sprint-testkit.svg)](https://pypi.org/project/agent-sprint-testkit/)

## 🎯 Features

- **🧠 3-Tier Evaluation System**: From basic testing to PhD-level assessment
- **🔬 Rigorous Multi-Layer Evaluation**: Professional-grade assessment using multiple OpenAI evaluators
- **📊 Performance Metrics**: Comprehensive analysis with response time, success rate, and quality scoring
- **🔧 Easy Installation**: Simple pip install from PyPI with full cross-platform support
- **🌐 Universal Testing**: Works with CLI agents, REST APIs, Python modules, and more
- **🤖 Agent Ready**: Compatible with LangChain, OpenAI, and custom agents
- **📁 Built-in Examples**: File Q&A agent and project templates included
- **⚙️ GitHub Actions**: Ready-to-use CI/CD workflow templates
- **🎯 OpenAI Evals Integration**: Enterprise-grade evaluation using OpenAI's infrastructure
- **💰 Cost Management**: Built-in cost estimation and budgeting controls

## 📊 Evaluation Tiers

ASTK provides three distinct testing tiers to meet different development and assessment needs:

| Tier                           | Purpose               | Cost  | Time      | Pass Rate | Use Case                        |
| ------------------------------ | --------------------- | ----- | --------- | --------- | ------------------------------- |
| **🟢 TIER 1<br>Basic Testing** | Development feedback  | FREE  | 2-3 min   | 80-100%   | Daily development iterations    |
| **🟡 TIER 2<br>Professional**  | Production validation | $1-5  | 5-10 min  | 60-80%    | Pre-deployment assessment       |
| **🔴 TIER 3<br>Rigorous**      | Expert assessment     | $7-15 | 10-20 min | 10-30%    | Research, competition, academic |

## 🚀 Quick Start

### 1. Installation

```bash
# Standard installation
pip install agent-sprint-testkit

# With OpenAI Evals support for rigorous evaluation
pip install agent-sprint-testkit[evals]
```

### 2. Setup API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Initialize Project

```bash
python -m astk.cli init my-agent-tests
cd my-agent-tests
```

### 4. Run Your First Evaluation

```bash
# Tier 1: Basic Testing (FREE)
python -m astk.cli benchmark examples/agents/file_qa_agent.py

# Tier 2: Professional Evaluation ($1-5)
python -m astk.cli evals create my_agent.py --eval-type code_qa

# Tier 3: Rigorous Multi-Layer Assessment ($7-15)
python -m astk.cli rigorous run my_agent.py --max-cost 10.0
```

## 🔬 Rigorous Multi-Layer Evaluation

Our flagship feature provides professional-grade AI agent assessment using multiple specialized OpenAI evaluators.

### ✨ Key Features

- **🎯 Multiple Evaluation Layers**: Each scenario uses 2-4 different OpenAI models as specialized evaluators
- **🏆 Expert-Level Assessment**: 4-tier difficulty system from foundational to expert integration
- **🧠 Domain-Specific Grading**: Specialized evaluation prompts for security, ethics, systems thinking, etc.
- **📊 Comprehensive Scoring**: Detailed dimension scores with weighted overall assessment
- **💰 Cost Transparent**: Built-in cost estimation and budgeting controls
- **⚡ Parallel Execution**: Optional parallel processing for faster results

### 🎯 Evaluation Tiers

| Tier          | Difficulty   | Focus                                          | Scenarios   | Pass Threshold |
| ------------- | ------------ | ---------------------------------------------- | ----------- | -------------- |
| **🎯 Tier 1** | Foundational | Mathematical reasoning, Technical explanations | 2 scenarios | 7.0+           |
| **🧠 Tier 2** | Advanced     | Creative problem-solving, Ethical dilemmas     | 2 scenarios | 7.5+           |
| **⚡ Tier 3** | Expert       | Systems analysis, Security assessment          | 2 scenarios | 8.0+           |
| **🚀 Tier 4** | Extreme      | Logical paradoxes, Crisis coordination         | 2 scenarios | 8.5+           |
| **💥 Chaos**  | Adversarial  | Prompt injection resistance                    | 1 scenario  | 9.0+           |

### 🚀 Quick Rigorous Evaluation

```bash
# Basic rigorous evaluation
python -m astk.cli rigorous run my_agent.py

# Development-friendly (lower cost)
python -m astk.cli rigorous run my_agent.py --max-cost 3.0 --fail-fast

# Professional assessment (parallel execution)
python -m astk.cli rigorous run my_agent.py \
  --evaluators gpt-4 o1-preview gpt-4-turbo \
  --max-cost 15.0 \
  --parallel \
  --output-format detailed \
  --save-results
```

### 💰 Cost Management

```bash
# Set cost limits
python -m astk.cli rigorous run my_agent.py --max-cost 10.0

# Use cost-effective evaluator combinations
python -m astk.cli rigorous run my_agent.py --evaluators gpt-4

# Quick development testing
python -m astk.cli rigorous run my_agent.py --max-cost 2.0 --fail-fast
```

**Estimated Costs:**

- Complete rigorous suite (9 scenarios): ~$6.50
- Single expert scenario: ~$0.50-$1.30
- Foundational scenarios: ~$0.30-$0.40

## 🎯 OpenAI Evals Integration

Professional-grade agent evaluation using OpenAI's enterprise infrastructure.

### ✨ Features

- **🏆 Enterprise-grade evaluation** using OpenAI's infrastructure
- **🎯 AI-powered grading** with detailed scoring explanations
- **⚖️ Easy A/B testing** between agent versions
- **📊 Comparative analysis** with industry benchmarks

### 🛠️ Quick Start

```bash
# Create evaluation for your agent
python -m astk.cli evals create my_agent.py --eval-type code_qa --grader gpt-4

# Run evaluation
python -m astk.cli evals run eval_12345

# Compare two models
python -m astk.cli evals compare eval_12345 gpt-4o-mini gpt-4-turbo
```

## 📋 Complete CLI Reference

### ✅ Reliable Command Format

**Always use this format for 100% reliability across all environments:**

```bash
python -m astk.cli <command>
```

This format works regardless of PATH configuration, virtual environments, or installation method.

### Core Commands

```bash
# Show comprehensive help with all tiers
python -m astk.cli --help

# Initialize new project with templates
python -m astk.cli init <project-name>

# Run basic benchmarks (Tier 1)
python -m astk.cli benchmark <agent-path>

# Show examples and tier guide
python -m astk.cli examples

# Generate reports
python -m astk.cli report <results-dir>
```

### Rigorous Multi-Layer Evaluation

```bash
# Complete rigorous evaluation suite
python -m astk.cli rigorous run <agent-path>

# Custom evaluation with specific parameters
python -m astk.cli rigorous run <agent-path> \
  --scenarios path/to/scenarios.yaml \
  --evaluators gpt-4 o1-preview gpt-4-turbo \
  --parallel \
  --max-cost 20.0 \
  --output-format detailed \
  --save-results \
  --fail-fast

# Available options:
# --scenarios: Custom scenarios YAML file
# --evaluators: OpenAI models (gpt-4, o1-preview, gpt-4-turbo)
# --parallel: Run scenarios in parallel (faster, more expensive)
# --max-cost: Maximum total cost in USD
# --output-format: json, yaml, or detailed markdown
# --save-results: Save comprehensive results to file
# --fail-fast: Stop on first scenario failure
# --retry-failures: Number of retry attempts (default: 1)
```

### OpenAI Evals Integration

```bash
# Create professional evaluation
python -m astk.cli evals create <agent-path> --eval-type code_qa --grader gpt-4

# Run evaluation from logs
python -m astk.cli evals run <eval-id>

# Compare two models
python -m astk.cli evals compare <eval-id> baseline-model test-model

# Available eval types: general, code_qa, customer_service, research
# Available graders: gpt-4, gpt-4-turbo, o3, o3-mini
```

## 🤖 Creating Your Agent

Your agent must accept queries as command-line arguments:

```python
#!/usr/bin/env python3
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
```

**Test your agent:**

```bash
# Make sure your agent works
python my_agent.py "What is 2+2?"

# Then run ASTK evaluation
python -m astk.cli benchmark my_agent.py
```

## 🧪 Example Scenarios

### Basic Benchmark (Tier 1)

Tests 8 fundamental capabilities:

- **📁 File Discovery**: Find Python files and entry points
- **⚙️ Config Analysis**: Analyze configuration files
- **📖 README Comprehension**: Read and explain project documentation
- **🏗️ Code Structure**: Analyze directory architecture
- **📚 Documentation Search**: Explore project documentation
- **🔗 Dependency Analysis**: Analyze requirements and dependencies
- **💡 Example Exploration**: Discover example implementations
- **🧪 Test Discovery**: Find testing frameworks and patterns

### Rigorous Multi-Layer Scenarios (Tier 3)

**Foundational Reasoning** - Multi-step mathematical problem with verification:

- Tests calculation accuracy and step-by-step reasoning
- Multiple evaluators verify mathematical correctness

**Creative Constraint Problem** - Design offline food delivery app:

- Evaluates innovation within severe technical constraints
- Cultural sensitivity and business viability assessment

**Ethical AI Dilemma** - Healthcare ICU bed allocation:

- Tests ethical reasoning and moral framework application
- Legal compliance and practical implementation evaluation

**Complex Systems Analysis** - Universal Basic Income impact:

- 6-domain analysis across economic, social, political dimensions
- Systems thinking with feedback loop identification

**Adversarial Security Analysis** - Cryptocurrency exchange security:

- Security expertise and threat modeling evaluation
- Risk assessment and mitigation strategy analysis

**Crisis Coordination** - Multi-modal disaster response:

- Hurricane + COVID + cyberattack simultaneous crisis
- Resource allocation and stakeholder coordination

**Logical Paradoxes** - AI self-reference and consistency:

- Tests handling of logical contradictions
- Philosophical reasoning and consistency evaluation

**Prompt Injection Resistance** - Adversarial input testing:

- Security robustness against manipulation attempts
- Attack resistance and safe response generation

## 📊 Results & Analysis

### Comprehensive Metrics

ASTK provides detailed analysis across multiple dimensions:

```json
{
  "success_rate": 0.78,
  "complexity_score": 0.65,
  "total_duration_seconds": 45.2,
  "average_response_length": 1247,
  "difficulty_breakdown": {
    "foundational": { "success_rate": 1.0, "scenarios": "2/2" },
    "advanced": { "success_rate": 0.6, "scenarios": "3/5" },
    "expert": { "success_rate": 0.4, "scenarios": "2/5" }
  },
  "category_breakdown": {
    "reasoning": { "success_rate": 0.67, "scenarios": "2/3" },
    "creativity": { "success_rate": 0.5, "scenarios": "1/2" },
    "ethics": { "success_rate": 1.0, "scenarios": "2/2" },
    "security": { "success_rate": 0.3, "scenarios": "1/3" }
  }
}
```

### AI Capability Assessment

Based on **Complexity Score**:

- **🌟 Exceptional AI (80%+)**: Expert-level reasoning across multiple domains
- **🔥 Advanced AI (60-79%)**: Strong performance on sophisticated tasks
- **💡 Competent AI (40-59%)**: Good basic capabilities, room for improvement
- **📚 Developing AI (<40%)**: Focus on foundational skills

## 🏗️ Project Structure

```
ASTK/
├── 🤖 examples/
│   ├── agents/                  # Example AI agents
│   │   └── file_qa_agent.py     # LangChain File Q&A agent
│   └── benchmarks/scenarios/    # Evaluation scenarios
│       └── rigorous_multilayer_scenarios.yaml  # Expert scenarios
├── 📊 scripts/                  # Benchmark and utility scripts
│   ├── simple_benchmark.py      # Intelligent benchmark runner
│   ├── simple_run.py            # Basic agent runner
│   └── astk.py                  # Advanced CLI
├── 🧠 astk/                     # Core ASTK framework
│   ├── benchmarks/              # Benchmark modules
│   ├── cli.py                   # Command-line interface
│   ├── evals_integration.py     # OpenAI Evals integration
│   ├── schema.py                # Data schemas
│   └── *.py                     # Core modules
├── 📁 benchmark_results/        # Generated benchmark results
├── ⚙️ config/                   # Configuration files
└── 📖 docs/                     # Documentation
```

## 🎮 Usage Examples

### Daily Development Workflow

```bash
# Quick development testing (FREE)
python -m astk.cli benchmark my_agent.py

# Check specific capabilities
python -m astk.cli benchmark my_agent.py --scenarios 5

# View results
python -m astk.cli report astk_results/
```

### Pre-Production Assessment

```bash
# Professional evaluation
python -m astk.cli evals create my_agent.py --eval-type code_qa

# Run comprehensive assessment
python -m astk.cli evals run eval_12345
```

### Research & Competition

```bash
# Complete rigorous evaluation
python -m astk.cli rigorous run my_agent.py --max-cost 15.0

# Parallel execution for speed
python -m astk.cli rigorous run my_agent.py \
  --parallel \
  --evaluators gpt-4 o1-preview gpt-4-turbo \
  --save-results
```

### CI/CD Integration

```yaml
# .github/workflows/astk.yml
name: ASTK Agent Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install ASTK
        run: pip install agent-sprint-testkit[evals]

      - name: Run Basic Benchmarks
        run: python -m astk.cli benchmark agents/my_agent.py

      - name: Run Professional Evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -m astk.cli rigorous run agents/my_agent.py \
            --max-cost 5.0 \
            --fail-fast \
            --save-results

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-results
          path: rigorous_evaluation_*.json
```

## 🔧 Troubleshooting

### Installation Issues

```bash
# Update pip and reinstall
pip install --upgrade pip
pip install --upgrade agent-sprint-testkit[evals]

# Verify installation
python -m astk.cli --version
python -c "import astk; print('ASTK loaded successfully')"
```

### CLI Command Issues

**✅ Always use the reliable format:**

```bash
# Recommended (always works)
python -m astk.cli benchmark my_agent.py

# Avoid (may fail with PATH issues)
astk benchmark my_agent.py
```

### OpenAI API Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Set API key
export OPENAI_API_KEY="sk-..."

# Test API access
python -c "import openai; print('OpenAI client ready')"
```

### Cost Management for Rigorous Evaluation

```bash
# Set strict cost limits
python -m astk.cli rigorous run my_agent.py --max-cost 5.0

# Use fewer evaluators to reduce costs
python -m astk.cli rigorous run my_agent.py --evaluators gpt-4

# Development testing with fail-fast
python -m astk.cli rigorous run my_agent.py --max-cost 2.0 --fail-fast
```

### Agent Compatibility

**Your agent must:**

- Accept queries as command-line arguments
- Print responses to stdout
- Exit with code 0 on success

**Test your agent:**

```bash
python your_agent.py "test question"
# Should print a response and exit cleanly
```

## 📈 Performance Tips

- **⚡ Faster Responses**: Optimize your agent's processing pipeline
- **🧠 Better Intelligence**: Use more sophisticated reasoning patterns
- **💰 Cost Optimization**: Use `--max-cost` limits and selective evaluators
- **🔧 Custom Scenarios**: Create domain-specific evaluation scenarios
- **⚡ Parallel Processing**: Use `--parallel` for faster rigorous evaluation
- **🎯 Targeted Testing**: Focus on specific capability categories

## 🤝 Contributing

1. **Fork the repository** and create a feature branch
2. **Add new agents** in `examples/agents/`
3. **Create new scenarios** in `examples/benchmarks/scenarios/`
4. **Test thoroughly** with all evaluation tiers
5. **Submit pull request** with comprehensive test results

## 📄 License

Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License

For commercial use or derivative works, please contact: admin@blackbox-dev.com  
See LICENSE file for complete details.

---

## 🚀 Get Started Now

```bash
# Quick installation and first test
pip install agent-sprint-testkit[evals]
export OPENAI_API_KEY="your-key"
python -m astk.cli init my-tests
cd my-tests
python -m astk.cli examples

# Run first evaluation
python -m astk.cli benchmark examples/agents/file_qa_agent.py

# Try rigorous assessment
python -m astk.cli rigorous run examples/agents/file_qa_agent.py --max-cost 3.0
```

**Ready to evaluate your AI agent?** Start with basic testing and progress through our three-tier system as your agent improves!

📚 **For package-specific installation and usage instructions, see [README-PACKAGE.md](README-PACKAGE.md)**
