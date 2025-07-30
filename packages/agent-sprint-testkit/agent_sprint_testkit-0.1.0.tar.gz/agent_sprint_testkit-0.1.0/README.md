# AgentSprint TestKit (ASTK) 🚀

> Benchmark your AI agents with intelligent, diverse test scenarios

ASTK is a comprehensive testing framework for AI agents that evaluates performance, intelligence, and capabilities through diverse scenarios. Test your agents against real-world tasks like file analysis, code comprehension, and complex reasoning.

## 🎯 Features

- **🧠 Intelligent Benchmarks**: 8 diverse scenarios testing different AI capabilities
- **📊 Performance Metrics**: Response time, success rate, and quality analysis
- **🔧 Easy Setup**: Simple Python environment with minimal dependencies
- **🤖 Agent Ready**: Works with LangChain, OpenAI, and custom agents
- **📁 File Q&A Agent**: Built-in example agent for testing

## 📋 Quick Start

### 1. Prerequisites

- Python 3.11+
- OpenAI API Key

### 2. Setup Environment

```bash
# Clone/navigate to ASTK directory
cd /path/to/ASTK

# Create and activate virtual environment
python3.11 -m venv .venv311
source .venv311/bin/activate  # On Windows: .venv311\Scripts\activate

# Install dependencies
pip install langchain langchain-openai langchain-core pydantic click psutil
```

### 3. Set API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 4. Run Your First Benchmark

```bash
# Run the intelligent benchmark on the example agent
python scripts/simple_benchmark.py examples/agents/file_qa_agent.py
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

### 🚀 Simple Benchmark Runner

```bash
python scripts/simple_benchmark.py <agent_path>
```

Runs 8 intelligent scenarios and generates detailed performance reports.

### 🔧 Simple Agent Runner

```bash
python scripts/simple_run.py <agent_path>
```

Runs an agent directly with basic output capture.

### 📋 ASTK CLI (Advanced)

```bash
# Initialize project structure
python scripts/astk.py init

# Run advanced benchmarks (when package issues resolved)
python scripts/astk.py run <agent_path>

# View results
python scripts/astk.py view <results_dir>
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

**🐍 Virtual Environment Problems**

```bash
# Recreate environment
deactivate
rm -rf .venv311
python3.11 -m venv .venv311
source .venv311/bin/activate
pip install langchain langchain-openai langchain-core pydantic
```

**🔑 OpenAI API Issues**

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Set API key
export OPENAI_API_KEY="sk-..."
```

**📦 Import Errors**

```bash
# Install missing packages
pip install langchain langchain-openai langchain-core pydantic click psutil

# Verify installation
python -c "from langchain_openai import ChatOpenAI; print('✅ LangChain installed')"
```

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
python scripts/simple_benchmark.py examples/agents/file_qa_agent.py
```
