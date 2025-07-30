# AgentSprint TestKit (ASTK) 🚀

> Universal AI agent benchmarking and testing framework

ASTK is a comprehensive testing framework for AI agents that evaluates performance, intelligence, and capabilities through diverse scenarios. Test your agents against real-world tasks like file analysis, code comprehension, and complex reasoning.

## Usage Example

Please see https://github.com/StanHus/astk-test

## 🎯 Features

- **🧠 Intelligent Benchmarks**: 8 diverse scenarios testing different AI capabilities
- **📊 Performance Metrics**: Response time, success rate, and quality analysis
- **🔧 Easy Installation**: Simple pip install from PyPI
- **🌐 Universal Testing**: Works with CLI agents, REST APIs, Python modules, and more
- **🤖 Agent Ready**: Compatible with LangChain, OpenAI, and custom agents
- **📁 Built-in Examples**: File Q&A agent and project templates
- **⚙️ GitHub Actions**: Ready-to-use CI/CD workflow templates
- **🎯 OpenAI Evals Integration**: Professional-grade evaluation using OpenAI's infrastructure (Beta)

## 📋 Quick Start

### 1. Install from PyPI

```bash
# Standard installation
pip install agent-sprint-testkit

# With OpenAI Evals support (Beta)
pip install agent-sprint-testkit[evals]
```

### 2. Verify Installation

```bash
python -m astk.cli --help
```

### 3. Set API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 4. Initialize a Project

```bash
python -m astk.cli init my-agent-tests
cd my-agent-tests
```

### 5. Run Your First Benchmark

```bash
# Traditional ASTK benchmark
python -m astk.cli benchmark examples/agents/file_qa_agent.py

# NEW: Professional evaluation with OpenAI Evals (Beta)
python -m astk.cli evals create my_agent.py --eval-type code_qa --grader gpt-4
```

## 🚀 Installation Options

### Option 1: Global Installation (Recommended)

```bash
# Standard installation
pip install agent-sprint-testkit

# With all optional features
pip install agent-sprint-testkit[evals,dev,docker]
```

### Option 2: Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/astk.git
cd astk

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[evals,dev]
```

## 💻 CLI Commands

### Core Commands

```bash
# Initialize new project with templates
python -m astk.cli init <project-name>

# Run intelligent benchmarks
python -m astk.cli benchmark <agent-path>

# Generate detailed reports
python -m astk.cli report <results-dir>

# Show example usage
python -m astk.cli examples
```

### 🎯 OpenAI Evals Integration (Beta)

```bash
# Create professional evaluation
python -m astk.cli evals create my_agent.py --eval-type code_qa --grader gpt-4

# Run evaluation from logs
python -m astk.cli evals run <eval-id>

# Compare two models
python -m astk.cli evals compare <eval-id> gpt-4o-mini gpt-4-turbo

# Available eval types: general, code_qa, customer_service, research
# Available graders: gpt-4, gpt-4-turbo, o3, o3-mini
```

### Legacy Script Commands (still supported)

```bash
# Run intelligent benchmark
python scripts/simple_benchmark.py <agent-path>

# Quick agent runner
python scripts/simple_run.py <agent-path>
```

## 🎯 OpenAI Evals Integration (Beta)

ASTK now integrates with OpenAI's professional Evals API for enterprise-grade agent evaluation:

### ✨ Key Benefits

- **🏆 Professional-grade evaluation** using OpenAI's infrastructure
- **🎯 AI-powered grading** with detailed scoring explanations
- **⚖️ Easy A/B testing** between agent versions
- **📊 Comparative analysis** with industry benchmarks
- **💰 Cost-effective** by leveraging existing logs

### 🛠️ Quick Start with Evals

```bash
# 1. Install with Evals support
pip install agent-sprint-testkit[evals]

# 2. Set up OpenAI API key
export OPENAI_API_KEY=your_key_here

# 3. Create evaluation for your agent
python -m astk.cli evals create my_agent.py --eval-type code_qa --grader gpt-4

# 4. Run evaluation
python -m astk.cli evals run eval_12345

# 5. View results in OpenAI dashboard
```

### 📊 Evaluation Types

| Type               | Description                 | Use Case                         |
| ------------------ | --------------------------- | -------------------------------- |
| `general`          | General-purpose evaluation  | All-around agent testing         |
| `code_qa`          | Code analysis and Q&A       | Developer tools, code assistants |
| `customer_service` | Customer support scenarios  | Support bots, help systems       |
| `research`         | Research and analysis tasks | Research assistants, analysts    |

### 🎓 Example Usage

```python
# Create and run evaluation programmatically
from astk.evals_integration import OpenAIEvalsAdapter

adapter = OpenAIEvalsAdapter()
eval_id = adapter.create_eval_from_scenarios(
    scenarios=my_scenarios,
    eval_name="My Agent Evaluation",
    grader_model="gpt-4"
)

# Run comparative evaluation
results = adapter.run_comparative_evaluation(
    eval_id=eval_id,
    baseline_model="gpt-4o-mini",
    test_model="gpt-4-turbo"
)
```

## 🤖 Available Agents

### File Q&A Agent (`examples/agents/file_qa_agent.py`)

A LangChain-powered agent that can:

- **📁 List files** in directories
- **📖 Read file contents** and summarize
- **🔍 Answer questions** about file data
- **🧭 Navigate** directory structures

**Example Usage:**

```bash
# Direct agent usage
python examples/agents/file_qa_agent.py "What Python files are in this project?"

# Run with simple runner
python scripts/simple_run.py examples/agents/file_qa_agent.py

# Run intelligent benchmark
python scripts/simple_benchmark.py examples/agents/file_qa_agent.py
```

## 🧪 Benchmark Scenarios

The intelligent benchmark tests 8 diverse scenarios:

| Scenario                    | Test                               | Capability                 |
| --------------------------- | ---------------------------------- | -------------------------- |
| **📁 File Discovery**       | Find Python files and entry points | File system navigation     |
| **⚙️ Config Analysis**      | Analyze configuration files        | Technical comprehension    |
| **📖 README Comprehension** | Read and explain project           | Document analysis          |
| **🏗️ Code Structure**       | Analyze directory structure        | Architecture understanding |
| **📚 Documentation Search** | Explore documentation              | Information retrieval      |
| **🔗 Dependency Analysis**  | Analyze requirements/dependencies  | Technical analysis         |
| **💡 Example Exploration**  | Discover example code              | Code comprehension         |
| **🧪 Test Discovery**       | Find testing framework             | Development understanding  |

## 📊 Results & Metrics

Benchmarks generate comprehensive results:

```json
{
  "success_rate": 1.0,
  "total_duration_seconds": 25.4,
  "average_scenario_duration": 3.2,
  "average_response_length": 847,
  "scenarios": [...]
}
```

**Metrics Include:**

- ✅ **Success Rate**: Percentage of completed scenarios
- ⏱️ **Response Time**: Duration for each scenario
- 📝 **Response Quality**: Length and content analysis
- 🎯 **Scenario Details**: Individual query results

## 🛠️ Available Tools

### 🚀 ASTK CLI (Primary Interface)

```bash
# Initialize project with templates
python -m astk.cli init my-project

# Run intelligent benchmarks
python -m astk.cli benchmark <agent-path>

# Generate HTML/JSON reports
python -m astk.cli report <results-dir>

# View usage examples
python -m astk.cli examples
```

### 🧪 Legacy Script Runners (Still Supported)

```bash
# Direct benchmark execution
python scripts/simple_benchmark.py <agent-path>

# Basic agent runner
python scripts/simple_run.py <agent-path>
```

## 🏗️ Project Structure

```
ASTK/
├── 🤖 examples/agents/          # Example AI agents
│   └── file_qa_agent.py         # LangChain File Q&A agent
├── 📊 scripts/                  # Benchmark and utility scripts
│   ├── simple_benchmark.py      # Intelligent benchmark runner ⭐
│   ├── simple_run.py            # Basic agent runner
│   └── astk.py                  # Advanced CLI (WIP)
├── 🧠 astk/                     # Core ASTK framework
│   ├── benchmarks/              # Benchmark modules
│   ├── cli.py                   # Command-line interface
│   └── *.py                     # Core modules
├── 📁 benchmark_results/        # Generated benchmark results
├── ⚙️ config/                   # Configuration files
└── 📖 docs/                     # Documentation
```

## 🎮 Usage Examples

### Run Agent Directly

```bash
python examples/agents/file_qa_agent.py "Analyze the setup.py file"
```

### Quick Agent Test

```bash
python scripts/simple_run.py examples/agents/file_qa_agent.py
```

### Full Intelligence Benchmark

```bash
python scripts/simple_benchmark.py examples/agents/file_qa_agent.py
```

### Custom Queries

```bash
python examples/agents/file_qa_agent.py "What is the purpose of the astk directory?"
```

## 🔧 Troubleshooting

### Common Issues

**📦 Installation Problems**

```bash
# Update pip and reinstall
pip install --upgrade pip
pip install --upgrade agent-sprint-testkit

# Verify installation
python -m astk.cli --version
python -c "import astk; print('ASTK loaded successfully')"
```

**🛠️ CLI Command Issues**

For 100% reliable CLI usage that works across all environments:

```bash
# Always use this format (recommended)
python -m astk.cli benchmark examples/agents/file_qa_agent.py

# Instead of this (may fail with PATH issues)
astk benchmark examples/agents/file_qa_agent.py
```

📖 **See [RELIABLE_CLI_USAGE.md](RELIABLE_CLI_USAGE.md) for complete CLI guidance**

**🔑 OpenAI API Issues**

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Set API key
export OPENAI_API_KEY="sk-..."
```

**🐍 Development Environment Issues**

```bash
# For development setup
git clone https://github.com/your-org/astk.git
cd astk
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**🤖 Agent Compatibility**

The framework supports multiple agent types:

- **CLI agents**: Accept queries as command-line arguments
- **Python modules**: Have a `chat()` method
- **REST APIs**: Expose `/chat` endpoint
- **Custom formats**: Use adapter patterns as needed

## 🚀 Creating Your Own Agent

Create a new agent that responds to command-line arguments:

```python
#!/usr/bin/env python3
import sys

async def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        # Process query and return response
        print(f"Agent: {response}")
    else:
        # Default behavior
        print("Agent: Ready!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

Then benchmark it:

```bash
python scripts/simple_benchmark.py path/to/your_agent.py
```

## 📈 Performance Tips

- **⚡ Faster Responses**: Use GPT-3.5-turbo for speed
- **🧠 Better Intelligence**: Use GPT-4 for complex reasoning
- **💰 Cost Optimization**: Monitor token usage in results
- **🔧 Custom Scenarios**: Modify `scripts/simple_benchmark.py` for specific tests

## 🤝 Contributing

1. Create new agents in `examples/agents/`
2. Add benchmark scenarios in `scripts/simple_benchmark.py`
3. Test with: `python scripts/simple_benchmark.py your_agent.py`

## 📄 License

Apache 2.0 License - See LICENSE file for details.

---

**🎯 Ready to benchmark your AI agents? Start with:**

```bash
# Install globally
pip install agent-sprint-testkit

# Run your first benchmark
python -m astk.cli benchmark examples/agents/file_qa_agent.py

# Or use the legacy script
python scripts/simple_benchmark.py examples/agents/file_qa_agent.py
```

**🚀 Get started in 3 commands:**

```bash
pip install agent-sprint-testkit
python -m astk.cli init my-tests
python -m astk.cli examples
```
