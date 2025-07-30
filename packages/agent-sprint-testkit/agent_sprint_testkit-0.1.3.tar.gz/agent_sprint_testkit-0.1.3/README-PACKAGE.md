# ASTK Package Usage Guide 📖

> **Step-by-step instructions for using AgentSprint TestKit**

This guide shows you exactly how to install and use ASTK to test your AI agents. No technical background required!

## 🚀 What is ASTK?

ASTK is a tool that **tests your AI chatbots and agents** to see how well they work. Think of it like a "test suite" for your AI - it asks your agent different questions and measures how good the responses are.

## 📦 Step 1: Install ASTK

Open your terminal/command prompt and run:

```bash
pip install agent-sprint-testkit
```

**✅ Check it worked:**

```bash
astk --help
```

You should see a help menu. If you get an error, see [Troubleshooting](#troubleshooting) below.

## 🔑 Step 2: Set Up OpenAI API Key

ASTK uses OpenAI to help evaluate your agent's responses. You need an API key:

1. **Get an API key** from [OpenAI](https://platform.openai.com/api-keys)
2. **Set the key** in your terminal:

```bash
# On Mac/Linux:
export OPENAI_API_KEY="sk-your-key-here"

# On Windows:
set OPENAI_API_KEY=sk-your-key-here
```

## 🏁 Step 3: Your First Test

### Option A: Test the Example Agent

ASTK comes with a built-in example agent for testing:

```bash
astk init my-first-test
cd my-first-test
astk benchmark examples/agents/file_qa_agent.py
```

This will:

- ✅ Create a test project
- ✅ Run 8 different scenarios
- ✅ Generate a detailed report
- ✅ Show you how well the agent performed

### Option B: Test Your Own Agent

If you have your own AI agent, you can test it:

```bash
astk benchmark path/to/your-agent.py
```

**Your agent must accept questions as command-line arguments:**

```bash
python your-agent.py "What is 2+2?"
# Should output: "Agent: 4" or similar
```

## 📊 Understanding Results

After running a benchmark, you'll see sophisticated results like:

```json
{
  "success_rate": 0.67,           // 67% of tests passed
  "complexity_score": 0.58,       // 58% difficulty-weighted score
  "total_duration_seconds": 45.2, // Took 45 seconds total
  "average_response_length": 1247, // Average response was 1,247 characters
  "difficulty_breakdown": {
    "intermediate": {"success_rate": 1.0, "scenarios": "2/2"},
    "advanced": {"success_rate": 0.6, "scenarios": "3/5"},
    "expert": {"success_rate": 0.4, "scenarios": "2/5"}
  },
  "category_breakdown": {
    "reasoning": {"success_rate": 0.67, "scenarios": "2/3"},
    "creativity": {"success_rate": 0.5, "scenarios": "1/2"},
    "ethics": {"success_rate": 1.0, "scenarios": "2/2"}
  },
  "scenarios": [...]              // Details for each test
}
```

**🎯 What this means:**

### Core Metrics

- **Success Rate**: Percentage of scenarios completed successfully
- **Complexity Score**: Difficulty-weighted performance (Expert = 3x, Advanced = 2x, Intermediate = 1x)
- **Duration**: How fast your agent responds to complex challenges
- **Response Length**: How detailed and comprehensive the answers are

### Advanced Analytics

- **🎓 Difficulty Breakdown**: Performance across challenge levels
  - 📘 **Intermediate**: Basic problem-solving tasks
  - 📙 **Advanced**: Complex multi-step reasoning
  - 📕 **Expert**: Cutting-edge AI capabilities
- **🏷️ Category Performance**: Strengths across different domains
  - 🧠 **Reasoning**: Logic and problem-solving
  - 🎨 **Creativity**: Innovation and design thinking
  - ⚖️ **Ethics**: Responsible AI practices
  - 🔗 **Integration**: System architecture skills

### 🌟 AI Capability Ratings

Based on your **Complexity Score**:

- **🌟 Exceptional AI (80%+)**: Expert-level reasoning across multiple domains
- **🔥 Advanced AI (60-79%)**: Strong performance on sophisticated tasks
- **💡 Competent AI (40-59%)**: Good basic capabilities, room for advanced improvement
- **📚 Developing AI (<40%)**: Focus on improving reasoning and problem-solving

## 🧪 What Tests Does ASTK Run?

ASTK automatically tests your agent with 12 sophisticated scenarios across multiple categories:

### 🧠 **Reasoning & Problem-Solving**

| Test                         | What it checks                                                                                              | Difficulty      |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------- |
| **Multi-step Reasoning**     | Can your agent analyze complex problems, identify security vulnerabilities, and provide detailed solutions? | 📙 Advanced     |
| **Edge Case Analysis**       | How well does it handle unusual situations, errors, and unexpected inputs?                                  | 📘 Intermediate |
| **Performance Optimization** | Can it analyze code for bottlenecks and suggest detailed performance improvements?                          | 📙 Advanced     |

### 🎨 **Creativity & Innovation**

| Test                             | What it checks                                                                                 | Difficulty |
| -------------------------------- | ---------------------------------------------------------------------------------------------- | ---------- |
| **Creative Problem Solving**     | Can your agent design new features and architectures from scratch with implementation details? | 📕 Expert  |
| **Adaptive Learning Assessment** | Can it design self-improving systems and machine learning approaches?                          | 📕 Expert  |

### 🔗 **System Integration & Architecture**

| Test                         | What it checks                                                      | Difficulty  |
| ---------------------------- | ------------------------------------------------------------------- | ----------- |
| **Cross-domain Integration** | How well can it design complete DevOps and CI/CD strategies?        | 📕 Expert   |
| **Failure Recovery Design**  | Can it create comprehensive error handling and reliability systems? | 📙 Advanced |
| **Scalability Architecture** | Can it redesign systems for massive scale (100k+ concurrent users)? | 📕 Expert   |

### ⚖️ **Ethics & Compliance**

| Test                      | What it checks                                                      | Difficulty  |
| ------------------------- | ------------------------------------------------------------------- | ----------- |
| **Ethical AI Evaluation** | Does it understand AI bias, fairness, and responsible AI practices? | 📙 Advanced |
| **Regulatory Compliance** | Can it design systems that meet GDPR, CCPA, and AI regulations?     | 📙 Advanced |

### 💼 **Strategic & Future-Tech Analysis**

| Test                            | What it checks                                                          | Difficulty      |
| ------------------------------- | ----------------------------------------------------------------------- | --------------- |
| **Competitive Analysis**        | Can it analyze markets, competitive positioning, and business strategy? | 📘 Intermediate |
| **Quantum Computing Readiness** | Does it understand emerging technologies and future-tech implications?  | 📕 Expert       |

### 📊 **New Metrics You'll Get:**

- **🧠 Complexity Score**: Difficulty-weighted performance (Expert tasks count 3x more than Intermediate)
- **🎓 Difficulty Breakdown**: How well your agent handles Intermediate vs Advanced vs Expert challenges
- **🏷️ Category Performance**: Which areas your agent excels in (Reasoning, Creativity, Ethics, etc.)
- **🏆 Best Category**: Your agent's strongest capability area
- **🌟 AI Capability Assessment**: Overall intelligence rating from "Developing" to "Exceptional"

## 🎯 Common Use Cases

### Testing a Simple Chatbot

```bash
# Your chatbot file: my_bot.py
#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        # Your chatbot logic here
        answer = f"Bot says: {question}"
        print(answer)

if __name__ == "__main__":
    main()
```

**Test it:**

```bash
astk benchmark my_bot.py
```

### Testing Different Agent Types

**CLI Agent (takes command line arguments):**

```bash
astk benchmark my_cli_agent.py
```

**Python Module Agent (has a chat method):**

```bash
# ASTK will automatically detect and use the chat() method
astk benchmark my_module_agent.py
```

**REST API Agent:**

```bash
# ASTK will try to use the /chat endpoint
astk benchmark http://localhost:8000
```

## 📋 All Available Commands

```bash
# Initialize a new test project
astk init <project-name>

# Run benchmark tests
astk benchmark <agent-path>

# Generate detailed reports
astk report <results-directory>

# Show examples and help
astk examples

# Show version
astk --version
```

## 🔧 Troubleshooting

### ❌ "Command not found: astk"

**Problem:** Package not installed properly

**Solution:**

```bash
pip install --upgrade pip
pip install agent-sprint-testkit
```

**Still not working?** Try:

```bash
python -m pip install agent-sprint-testkit
```

### ❌ "OpenAI API key not found"

**Problem:** API key not set

**Solution:**

```bash
# Check if it's set:
echo $OPENAI_API_KEY

# Set it:
export OPENAI_API_KEY="sk-your-key-here"
```

### ❌ "Agent failed to respond"

**Problem:** Your agent doesn't accept command-line arguments

**Solution:** Make sure your agent works like this:

```bash
python your-agent.py "test question"
# Should print something back
```

**Example working agent:**

```python
#!/usr/bin/env python3
import sys

if len(sys.argv) > 1:
    question = " ".join(sys.argv[1:])
    print(f"Agent: Here's my response to '{question}'")
else:
    print("Agent: Please ask me a question!")
```

### ❌ Permission errors

**Problem:** Can't install or run commands

**Solution:**

```bash
# Try with user installation:
pip install --user agent-sprint-testkit

# Add to PATH if needed:
export PATH=$PATH:~/.local/bin
```

## 🎮 Quick Examples

### 1. Basic Test Run

```bash
pip install agent-sprint-testkit
export OPENAI_API_KEY="your-key"
astk init test-project
cd test-project
astk benchmark examples/agents/file_qa_agent.py
```

### 2. Test Your Own Agent

```bash
# Create simple agent
echo '#!/usr/bin/env python3
import sys
if len(sys.argv) > 1:
    print(f"Bot: {sys.argv[1]}")' > my_bot.py

chmod +x my_bot.py

# Test it
astk benchmark my_bot.py
```

### 3. Multiple Tests

```bash
# Test different agents
astk benchmark agent1.py
astk benchmark agent2.py
astk benchmark http://localhost:8000

# Compare results
astk report benchmark_results/
```

## 📈 Improving Your Agent

Based on ASTK results, you can improve your agent:

- **Low success rate?** Make sure your agent handles different question types
- **Slow responses?** Optimize your agent's processing speed
- **Short responses?** Add more detailed explanations
- **Failed scenarios?** Test your agent with the specific question types ASTK uses

## 💡 Tips for Best Results

1. **Test regularly** - Run ASTK after every major change to your agent
2. **Check all scenarios** - Make sure your agent handles different types of questions
3. **Monitor performance** - Watch response times and success rates
4. **Use the reports** - ASTK generates detailed reports to help you improve

## 🚀 Next Steps

1. **Install ASTK**: `pip install agent-sprint-testkit`
2. **Set API key**: `export OPENAI_API_KEY="your-key"`
3. **Run first test**: `astk init test && cd test && astk examples`
4. **Test your agent**: `astk benchmark your-agent.py`
5. **Review results** and improve your agent!

---

**🎯 Ready to test your AI agent?**

```bash
pip install agent-sprint-testkit && astk --help
```

**Need help?** Check the [main documentation](README.md) or [open an issue](https://github.com/your-org/astk/issues).
