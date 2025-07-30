"""
OpenAI Evals API integration for ASTK
Prototype implementation for v0.2.0
"""

import os
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta

try:
    import openai
except ImportError:
    openai = None

from .schema import ScenarioConfig, SuccessCriteria


class OpenAIEvalsAdapter:
    """Adapter for integrating ASTK with OpenAI's Evals API"""

    def __init__(self, api_key: Optional[str] = None):
        if openai is None:
            raise ImportError(
                "OpenAI package required for Evals integration. Install with: pip install openai>=1.50.0")

        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.grader_prompts = GRADER_PROMPTS

    def create_eval_from_scenarios(
        self,
        scenarios: List[ScenarioConfig],
        eval_name: str = "ASTK Agent Evaluation",
        grader_model: str = "gpt-4"
    ) -> str:
        """
        Create an OpenAI Eval from ASTK scenarios

        Args:
            scenarios: List of ASTK scenario configurations
            eval_name: Name for the evaluation
            grader_model: Model to use for grading (gpt-4, o3, etc.)

        Returns:
            Evaluation ID
        """
        # Determine the appropriate grader prompt based on scenarios
        grader_prompt = self._select_grader_prompt(scenarios)

        eval_config = self.client.evals.create(
            name=eval_name,
            data_source_config={"type": "logs"},
            testing_criteria=[{
                "type": "score_model",
                "name": "ASTK Evaluator",
                "model": grader_model,
                "input": [
                    {"role": "system", "content": grader_prompt},
                    {"role": "user", "content": "{{item.input}}\n\nResponse to evaluate:\n{{sample.output_text}}"}
                ],
                "range": [1, 10],
                "pass_threshold": 6.0,
            }]
        )

        return eval_config.id

    def run_comparative_evaluation(
        self,
        eval_id: str,
        baseline_model: str,
        test_model: str,
        data_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Run comparative evaluation between two models

        Args:
            eval_id: ID of the evaluation to run
            baseline_model: Baseline model name
            test_model: Test model name
            data_limit: Number of samples to evaluate

        Returns:
            Dictionary with evaluation results
        """
        # Run baseline evaluation
        baseline_run = self.client.evals.runs.create(
            name=f"Baseline - {baseline_model}",
            eval_id=eval_id,
            data_source={
                "type": "responses",
                "source": {"type": "responses", "limit": data_limit},
            },
        )

        # Run test evaluation
        test_run = self.client.evals.runs.create(
            name=f"Test - {test_model}",
            eval_id=eval_id,
            data_source={
                "type": "responses",
                "source": {"type": "responses", "limit": data_limit},
                "input_messages": {
                    "type": "item_reference",
                    "item_reference": "item.input",
                },
                "model": test_model,
            },
        )

        return {
            "baseline_run": baseline_run,
            "test_run": test_run,
            "comparison_url": f"https://platform.openai.com/evals/compare/{baseline_run.id}/{test_run.id}"
        }

    def evaluate_from_logs(
        self,
        eval_id: str,
        days_back: int = 7,
        model_filter: Optional[str] = None
    ) -> str:
        """
        Evaluate agent performance based on logged responses

        Args:
            eval_id: ID of the evaluation to run
            days_back: Number of days back to look for logs
            model_filter: Optional model name to filter logs

        Returns:
            Run ID for the evaluation
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        data_source = {
            "type": "responses",
            "source": {
                "type": "responses",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }
        }

        if model_filter:
            data_source["source"]["model"] = model_filter

        run = self.client.evals.runs.create(
            name=f"Historical Evaluation - {days_back} days",
            eval_id=eval_id,
            data_source=data_source,
        )

        return run.id

    def _select_grader_prompt(self, scenarios: List[ScenarioConfig]) -> str:
        """Select appropriate grader prompt based on scenario types"""
        # Analyze scenarios to determine the best grader prompt
        task_types = [scenario.task for scenario in scenarios]

        if any("code" in task.lower() or "qa" in task.lower() for task in task_types):
            return self.grader_prompts["code_qa"]
        elif any("support" in task.lower() or "customer" in task.lower() for task in task_types):
            return self.grader_prompts["customer_service"]
        elif any("research" in task.lower() or "analysis" in task.lower() for task in task_types):
            return self.grader_prompts["research"]
        else:
            return self.grader_prompts["general"]


# Grader prompt templates for different agent types
GRADER_PROMPTS = {
    "code_qa": """
You are **Code-QA Grader**, an expert software engineer evaluating AI agent responses to code-related questions.

### Scoring Dimensions

1. **Technical Accuracy (40%)** 
   • Correctness of code analysis, API explanations, and technical concepts
   • Fact-check all technical claims; penalize hallucinations

2. **Completeness (30%)**
   • Coverage of relevant code components, dependencies, and functionality
   • Appropriate depth for the complexity of the code

3. **Clarity & Organization (20%)**
   • Well-structured, logical explanation that developers can follow
   • Good use of examples and clear language

4. **Practical Value (10%)**
   • Actionable insights, usage examples, or important context
   • Highlights potential issues or best practices

### Scoring Scale (1-10)
1-2: Major technical errors, misleading information
3-4: Some correct points but significant gaps or errors
5-6: Generally accurate with minor issues
7-8: Comprehensive and accurate explanation
9-10: Exceptional technical insight and clarity

Return JSON:
```json
{
  "steps": [
    {"description": "Technical accuracy assessment", "result": "8.0"},
    {"description": "Completeness evaluation", "result": "7.5"},
    {"description": "Clarity assessment", "result": "8.5"},
    {"description": "Practical value review", "result": "7.0"}
  ],
  "result": "7.8"
}
```
""",

    "customer_service": """
You are **Customer-Service Grader**, evaluating AI agent responses to customer inquiries.

### Scoring Dimensions

1. **Helpfulness & Problem-Solving (35%)**
   • Directly addresses the customer's issue or question
   • Provides actionable solutions or clear next steps

2. **Accuracy & Completeness (30%)**
   • Information is factually correct and comprehensive
   • Covers all aspects of the customer's inquiry

3. **Communication Quality (25%)**
   • Professional, empathetic, and clear tone
   • Appropriate language level for the customer

4. **Efficiency & Structure (10%)**
   • Concise while being thorough
   • Well-organized response that's easy to follow

### Scoring Scale (1-10)
1-2: Unhelpful, inaccurate, or inappropriate response
3-4: Partially helpful but with significant issues
5-6: Adequate response with room for improvement
7-8: Good customer service with minor areas for enhancement
9-10: Exceptional customer service that exceeds expectations

Return JSON with detailed assessment.
""",

    "research": """
You are **Research-Quality Grader**, evaluating AI agent responses for research and analysis tasks.

### Scoring Dimensions

1. **Information Quality & Accuracy (40%)**
   • Factual correctness and credibility of sources
   • Appropriate depth of research and analysis

2. **Analytical Reasoning (30%)**
   • Quality of insights, synthesis, and conclusions
   • Logical flow and evidence-based arguments

3. **Comprehensiveness (20%)**
   • Covers relevant aspects of the research topic
   • Identifies gaps or limitations appropriately

4. **Presentation & Organization (10%)**
   • Clear structure and professional presentation
   • Proper attribution and documentation

### Scoring Scale (1-10)
1-2: Poor research quality with major inaccuracies
3-4: Basic research with significant limitations
5-6: Adequate research meeting minimum standards
7-8: High-quality research with good analysis
9-10: Exceptional research demonstrating expert-level insight

Return JSON with detailed assessment.
""",

    "general": """
You are **General-Purpose Grader**, evaluating AI agent responses across various tasks.

### Scoring Dimensions

1. **Correctness & Accuracy (35%)**
   • Factual accuracy and appropriate responses
   • Absence of hallucinations or misleading information

2. **Completeness & Relevance (25%)**
   • Addresses all aspects of the query
   • Stays relevant to the user's needs

3. **Clarity & Communication (25%)**
   • Clear, well-organized, and understandable
   • Appropriate tone and language

4. **Usefulness & Insight (15%)**
   • Provides practical value to the user
   • Demonstrates understanding beyond surface level

### Scoring Scale (1-10)
1-2: Poor quality response with major issues
3-4: Below average with notable problems
5-6: Average response meeting basic expectations
7-8: Good quality response with minor issues
9-10: Excellent response demonstrating high capability

Return JSON with step-by-step assessment and final score.
"""
}


def convert_astk_to_evals_format(scenarios: List[ScenarioConfig]) -> Dict[str, Any]:
    """
    Convert ASTK scenarios to OpenAI Evals format

    This is a utility function for migration purposes
    """
    return {
        "scenarios": len(scenarios),
        "task_types": list(set(s.task for s in scenarios)),
        "protocols": list(set(s.protocol for s in scenarios)),
        "success_criteria_types": [
            type(s.success).__name__ for s in scenarios
        ]
    }
