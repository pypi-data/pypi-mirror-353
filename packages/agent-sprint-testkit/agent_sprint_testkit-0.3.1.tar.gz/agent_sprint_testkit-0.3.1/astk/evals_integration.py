"""
OpenAI Evals API integration for ASTK
Enhanced implementation for v0.2.0 with multi-layer evaluation support
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


class MultiLayerEvaluationResult:
    """Results from multi-layer OpenAI evaluation"""

    def __init__(self):
        self.layer_results = {}
        self.overall_score = 0.0
        self.passed = False
        self.detailed_feedback = {}
        self.evaluation_metadata = {}

    def add_layer_result(self, layer_name: str, score: float, feedback: str, evaluator: str):
        """Add result from a specific evaluation layer"""
        self.layer_results[layer_name] = {
            "score": score,
            "feedback": feedback,
            "evaluator": evaluator,
            "timestamp": datetime.now().isoformat()
        }

    def calculate_overall_score(self, weights: Optional[Dict[str, float]] = None):
        """Calculate weighted overall score from all layers"""
        if not self.layer_results:
            return 0.0

        if weights is None:
            # Equal weighting if no weights provided
            weights = {layer: 1.0 for layer in self.layer_results.keys()}

        total_score = 0.0
        total_weight = 0.0

        for layer, result in self.layer_results.items():
            weight = weights.get(layer, 1.0)
            total_score += result["score"] * weight
            total_weight += weight

        self.overall_score = total_score / total_weight if total_weight > 0 else 0.0
        return self.overall_score


class OpenAIEvalsAdapter:
    """Enhanced adapter for integrating ASTK with OpenAI's Evals API"""

    def __init__(self, api_key: Optional[str] = None):
        if openai is None:
            raise ImportError(
                "OpenAI package required for Evals integration. Install with: pip install openai>=1.50.0")

        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.grader_prompts = GRADER_PROMPTS
        self.evaluation_cache = {}

    def evaluate_response_multilayer(
        self,
        response: str,
        scenario_config: ScenarioConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> MultiLayerEvaluationResult:
        """
        Perform multi-layer evaluation of a response using multiple OpenAI evaluators

        Args:
            response: The agent response to evaluate
            scenario_config: The scenario configuration containing evaluation criteria
            context: Additional context for evaluation

        Returns:
            MultiLayerEvaluationResult with comprehensive evaluation
        """
        result = MultiLayerEvaluationResult()

        # Layer 1: Basic validation (regex, semantic)
        basic_score = self._evaluate_basic_criteria(
            response, scenario_config.success)
        result.add_layer_result("basic_validation", basic_score,
                                "Basic regex and semantic validation", "astk_basic")

        # Layer 2: OpenAI multi-evaluator assessment
        if hasattr(scenario_config.success, 'openai_evaluations'):
            for eval_config in scenario_config.success.openai_evaluations:
                evaluator_name = eval_config.evaluator
                prompt = eval_config.prompt
                pass_threshold = eval_config.pass_threshold

                # Perform OpenAI evaluation with error handling
                try:
                    eval_score, eval_feedback = self._perform_openai_evaluation(
                        response, prompt, evaluator_name, scenario_config, context
                    )

                    layer_name = f"openai_{evaluator_name}_{len(result.layer_results)}"
                    result.add_layer_result(
                        layer_name, eval_score, eval_feedback, evaluator_name)

                    # Track pass/fail for each layer
                    result.evaluation_metadata[layer_name] = {
                        "passed": eval_score >= pass_threshold,
                        "threshold": pass_threshold,
                        "evaluator_model": evaluator_name,
                        "status": "success"
                    }

                except Exception as e:
                    # Log the error but continue with other evaluators
                    layer_name = f"openai_{evaluator_name}_{len(result.layer_results)}"
                    error_message = f"EVALUATOR FAILED: {str(e)}"

                    # Add a failed evaluation result
                    result.add_layer_result(
                        layer_name, 0.0, error_message, evaluator_name)

                    # Track failure for each layer
                    result.evaluation_metadata[layer_name] = {
                        "passed": False,
                        "threshold": pass_threshold,
                        "evaluator_model": evaluator_name,
                        "status": "failed",
                        "error": str(e)
                    }

                    # Print warning for user visibility
                    print(
                        f"⚠️  Warning: Evaluator {evaluator_name} failed: {str(e)[:200]}...")

                    # If all evaluators are failing consistently, we might want to stop
                    # For now, continue to see which ones work

        # Calculate overall score and determine pass/fail
        result.calculate_overall_score()

        # Determine overall pass status (all critical layers must pass)
        result.passed = self._determine_overall_pass_status(
            result, scenario_config)

        return result

    def _perform_openai_evaluation(
        self,
        response: str,
        evaluation_prompt: str,
        evaluator_model: str,
        scenario_config: ScenarioConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[float, str]:
        """
        Perform a single OpenAI evaluation

        Returns:
            Tuple of (score, detailed_feedback)
        """

        # Construct the full evaluation prompt
        full_prompt = f"""
{evaluation_prompt}

SCENARIO CONTEXT:
- Task: {scenario_config.task}
- Difficulty: {getattr(scenario_config, 'difficulty', 'unknown')}
- Category: {getattr(scenario_config, 'category', 'general')}

AGENT RESPONSE TO EVALUATE:
{response}

Please provide your evaluation as JSON in the following format:
{{
    "overall_score": <score_1_to_10>,
    "dimension_scores": {{
        "dimension_1": <score>,
        "dimension_2": <score>,
        ...
    }},
    "detailed_feedback": "<comprehensive_explanation>",
    "strengths": ["<strength_1>", "<strength_2>", ...],
    "weaknesses": ["<weakness_1>", "<weakness_2>", ...],
    "recommendations": ["<rec_1>", "<rec_2>", ...]
}}
"""

        try:
            # Make the OpenAI API call
            response_obj = self.client.chat.completions.create(
                model=evaluator_model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator providing detailed, objective assessment of AI responses."},
                    {"role": "user", "content": full_prompt}
                ],
                # Low temperature for consistent evaluation
                temperature=1 if evaluator_model == "o4-mini" else 0.1,
            )

            evaluation_text = response_obj.choices[0].message.content

            if not evaluation_text or evaluation_text.strip() == "":
                raise ValueError(
                    f"Empty response from model {evaluator_model}")

            # Try to parse JSON response
            try:
                evaluation_data = json.loads(evaluation_text)
                score = float(evaluation_data.get("overall_score", 0))

                if score == 0:
                    raise ValueError(
                        f"Model {evaluator_model} returned score of 0 - likely evaluation failure")

                feedback = evaluation_data.get(
                    "detailed_feedback", evaluation_text)

                # Store complete evaluation data
                complete_feedback = {
                    "score": score,
                    "dimension_scores": evaluation_data.get("dimension_scores", {}),
                    "detailed_feedback": feedback,
                    "strengths": evaluation_data.get("strengths", []),
                    "weaknesses": evaluation_data.get("weaknesses", []),
                    "recommendations": evaluation_data.get("recommendations", []),
                    "raw_response": evaluation_text
                }

                return score, json.dumps(complete_feedback, indent=2)

            except json.JSONDecodeError as json_error:
                # Fallback: Extract numerical score from text
                try:
                    score = self._extract_score_from_text(
                        evaluation_text, evaluator_model)
                    return score, evaluation_text
                except ValueError as extract_error:
                    raise ValueError(
                        f"Model {evaluator_model} failed: JSON decode error: {json_error}, Score extraction error: {extract_error}, Response: {evaluation_text[:200]}...")

        except Exception as e:
            # Don't return 0.0 - raise the actual error so we can debug
            raise RuntimeError(
                f"OpenAI evaluation failed for model {evaluator_model}: {str(e)}")

    def _parse_openai_response(self, response_text: str, evaluator_model: str) -> float:
        """Parse OpenAI response to extract numerical score with improved error handling"""
        if not response_text or response_text.strip() == "":
            raise ValueError(f"Empty response from {evaluator_model}")

        try:
            # First try to parse as JSON
            response_json = json.loads(response_text)

            # Look for score in various common fields
            score_fields = ['overall_score', 'score',
                            'rating', 'evaluation_score', 'final_score']
            for field in score_fields:
                if field in response_json and isinstance(response_json[field], (int, float)):
                    score = float(response_json[field])
                    if 0 <= score <= 10:
                        return score

            # If JSON but no valid score field found
            raise ValueError(
                f"Valid score field not found in JSON response from {evaluator_model}")

        except json.JSONDecodeError:
            # If not JSON, try to extract numerical score from text
            return self._extract_score_from_text(response_text, evaluator_model)

    def _extract_score_from_text(self, text: str, evaluator_model: str) -> float:
        """Extract numerical score from text with model-specific handling"""
        import re

        # Enhanced patterns for different score formats
        patterns = [
            r'(?:overall_score|score|rating):\s*(\d+(?:\.\d+)?)',  # "score: 8.5"
            r'(?:overall_score|score|rating)\s*=\s*(\d+(?:\.\d+)?)',  # "score = 8.5"
            # "8.5/10" or "8.5 out of 10"
            r'(\d+(?:\.\d+)?)\s*(?:/\s*10|out\s+of\s+10)',
            r'(?:score|rating|evaluation).*?(\d+(?:\.\d+)?)',  # "My score is 8.5"
            # "I give it 8.5"
            r'(?:I\s+(?:give|rate|score)|rating|evaluation).*?(\d+(?:\.\d+)?)',
            # "8.5/10" or "8.5 points"
            r'\b(\d+(?:\.\d+)?)\s*(?:/10|points?)\b',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    score = float(match)
                    if 0 <= score <= 10:
                        return score
                except ValueError:
                    continue

        # Special handling for newer models that might use different formats
        if evaluator_model in ['gpt-4.1-mini', 'o4-mini']:
            # Try more flexible patterns for these models
            flexible_patterns = [
                r'(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(?:10|ten)',
                r'(?:score|rating|grade).*?(\d+(?:\.\d+)?)',
                # Score at end of line
                r'(\d+(?:\.\d+)?)(?:\s*(?:out of 10|/10))?$',
            ]

            for pattern in flexible_patterns:
                matches = re.findall(
                    pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        score = float(match)
                        if 0 <= score <= 10:
                            return score
                    except ValueError:
                        continue

        # If no score found, raise error with more context
        raise ValueError(
            f"Could not extract numerical score from {evaluator_model} evaluation. Response: {text[:200]}...")

    def _evaluate_basic_criteria(self, response: str, success_criteria: SuccessCriteria) -> float:
        """Evaluate basic regex and semantic criteria"""
        import re

        score = 0.0
        criteria_count = 0

        # Regex validation
        if success_criteria.regex:
            criteria_count += 1
            if re.search(success_criteria.regex, response, re.IGNORECASE):
                score += 10.0

        # Semantic score validation - use actual semantic similarity
        if success_criteria.semantic_score is not None:
            criteria_count += 1
            # Calculate actual semantic similarity using simple word overlap
            # This is basic but better than hardcoded values
            semantic_score = self._calculate_semantic_similarity(
                response, success_criteria)
            score += semantic_score

        if criteria_count == 0:
            raise ValueError("No basic criteria defined for evaluation")

        return score / criteria_count

    def _calculate_semantic_similarity(self, response: str, success_criteria: SuccessCriteria) -> float:
        """Calculate semantic similarity using basic text analysis"""
        # Simple approach: check for key domain-specific terms and response quality
        response_lower = response.lower()

        # Base score on response length and structure
        if len(response.strip()) < 50:
            base_score = 2.0  # Very short responses
        elif len(response.strip()) < 200:
            base_score = 5.0  # Short responses
        elif len(response.strip()) < 500:
            base_score = 7.0  # Medium responses
        else:
            base_score = 8.0  # Detailed responses

        # Adjust based on content quality indicators
        quality_indicators = [
            'because', 'therefore', 'however', 'although', 'moreover',
            'analysis', 'consider', 'recommendation', 'solution',
            'approach', 'strategy', 'implementation', 'evaluation'
        ]

        indicator_count = sum(
            1 for indicator in quality_indicators if indicator in response_lower)
        quality_bonus = min(indicator_count * 0.3, 2.0)  # Max 2 points bonus

        final_score = min(base_score + quality_bonus, 10.0)
        return final_score

    def _determine_overall_pass_status(
        self,
        result: MultiLayerEvaluationResult,
        scenario_config: ScenarioConfig
    ) -> bool:
        """Determine if the evaluation passes based on all layer requirements"""

        # Basic validation must pass
        basic_score = result.layer_results.get(
            "basic_validation", {}).get("score", 0)
        if basic_score < 6.0:  # Basic threshold
            return False

        # All OpenAI evaluations must meet their thresholds
        for layer_name, metadata in result.evaluation_metadata.items():
            if not metadata.get("passed", False):
                return False

        # Overall score threshold
        if result.overall_score < 7.0:  # Global minimum
            return False

        return True

    def create_eval_from_scenarios(
        self,
        scenarios: List[ScenarioConfig],
        eval_name: str = "ASTK Multi-Layer Agent Evaluation",
        grader_model: str = "gpt-4"
    ) -> str:
        """
        Create an OpenAI Eval from ASTK scenarios with multi-layer support

        Args:
            scenarios: List of ASTK scenario configurations
            eval_name: Name for the evaluation
            grader_model: Primary model to use for grading

        Returns:
            Evaluation ID
        """
        # Enhanced grader prompt that handles multi-layer evaluation
        grader_prompt = self._create_adaptive_grader_prompt(scenarios)

        eval_config = self.client.evals.create(
            name=eval_name,
            data_source_config={"type": "logs"},
            testing_criteria=[{
                "type": "score_model",
                "name": "ASTK Multi-Layer Evaluator",
                "model": grader_model,
                "input": [
                    {"role": "system", "content": grader_prompt},
                    {"role": "user", "content": "{{item.input}}\n\nResponse to evaluate:\n{{sample.output_text}}"}
                ],
                "range": [1, 10],
                "pass_threshold": 7.0,
                "multi_layer": True,
                "evaluation_dimensions": self._extract_evaluation_dimensions(scenarios)
            }]
        )

        return eval_config.id

    def _create_adaptive_grader_prompt(self, scenarios: List[ScenarioConfig]) -> str:
        """Create an adaptive grader prompt based on scenario complexity"""

        # Analyze scenario characteristics
        difficulties = [getattr(s, 'difficulty', 'intermediate')
                        for s in scenarios]
        categories = [getattr(s, 'category', 'general') for s in scenarios]

        expert_ratio = difficulties.count('expert') / len(difficulties)
        has_security = 'security' in categories
        has_ethics = 'ethics' in categories
        has_systems = 'systems_analysis' in categories

        base_prompt = """
You are **ASTK Multi-Layer Evaluator**, an expert AI assessment system designed to evaluate 
agent responses across multiple dimensions with professional rigor.

### Evaluation Approach

This evaluation uses a sophisticated multi-layer assessment framework:

1. **Technical Accuracy & Correctness (30%)**
   • Factual accuracy and logical soundness
   • Domain-specific knowledge demonstration
   • Absence of hallucinations or errors

2. **Depth & Comprehensiveness (25%)**  
   • Thorough coverage of the problem space
   • Appropriate level of detail for complexity
   • Addresses all aspects of the query

3. **Reasoning Quality (25%)**
   • Logical consistency and clear argumentation
   • Proper handling of complexity and nuance
   • Evidence-based conclusions

4. **Practical Value & Insight (20%)**
   • Actionable recommendations and insights
   • Real-world applicability
   • Professional-grade analysis
"""

        # Add specialized criteria based on scenario analysis
        if expert_ratio > 0.5:
            base_prompt += """
### Expert-Level Assessment Criteria

Given the expert-level complexity of these scenarios:
• Demonstrate deep domain expertise and sophisticated reasoning
• Show awareness of edge cases, trade-offs, and systemic implications  
• Provide novel insights beyond surface-level analysis
• Handle ambiguity and competing considerations expertly
"""

        if has_security:
            base_prompt += """
### Security Assessment Standards

For security-related evaluations:
• Assess threat model completeness and accuracy
• Evaluate defense-in-depth and risk mitigation strategies
• Consider adversarial perspectives and attack scenarios
• Verify compliance with security best practices
"""

        if has_ethics:
            base_prompt += """
### Ethical Reasoning Standards

For ethical scenarios:
• Evaluate moral reasoning framework soundness
• Assess consideration of competing ethical principles
• Check for bias awareness and stakeholder consideration
• Verify logical consistency in ethical conclusions
"""

        if has_systems:
            base_prompt += """
### Systems Thinking Standards

For complex systems analysis:
• Evaluate understanding of interconnections and feedback loops
• Assess consideration of second and third-order effects
• Check for systems-level perspective vs. reductionist thinking
• Verify scalability and sustainability considerations
"""

        base_prompt += """
### Scoring Guidelines (1-10 scale)

**9-10: Exceptional**
- Expert-level demonstration across all dimensions
- Novel insights and sophisticated reasoning
- Comprehensive and practically valuable

**7-8: Strong Performance**  
- Solid competency with minor gaps
- Good reasoning and practical value
- Meets professional standards

**5-6: Adequate**
- Basic requirements met with notable limitations
- Some gaps in reasoning or comprehensiveness
- Room for significant improvement

**1-4: Inadequate**
- Major deficiencies in accuracy or reasoning
- Incomplete or impractical responses
- Falls short of professional standards

Return detailed JSON evaluation with dimension scores and comprehensive feedback.
"""

        return base_prompt

    def _extract_evaluation_dimensions(self, scenarios: List[ScenarioConfig]) -> List[str]:
        """Extract evaluation dimensions from scenarios for metadata"""
        dimensions = set()

        for scenario in scenarios:
            if hasattr(scenario.success, 'openai_evaluations'):
                for eval_config in scenario.success.openai_evaluations:
                    # Extract dimension names from prompt if structured
                    prompt = eval_config.prompt
                    # Simple extraction - could be more sophisticated
                    if 'Technical Accuracy' in prompt:
                        dimensions.add('technical_accuracy')
                    if 'Completeness' in prompt:
                        dimensions.add('completeness')
                    if 'Innovation' in prompt or 'Creativity' in prompt:
                        dimensions.add('innovation')
                    if 'Ethics' in prompt or 'Ethical' in prompt:
                        dimensions.add('ethical_reasoning')
                    if 'Security' in prompt:
                        dimensions.add('security_analysis')
                    if 'Systems' in prompt:
                        dimensions.add('systems_thinking')

        return list(dimensions) if dimensions else ['accuracy', 'completeness', 'clarity', 'usefulness']

    def run_comparative_evaluation(
        self,
        eval_id: str,
        baseline_model: str,
        test_model: str,
        data_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Run comparative evaluation between two models with multi-layer analysis

        Args:
            eval_id: ID of the evaluation to run
            baseline_model: Baseline model name
            test_model: Test model name
            data_limit: Number of samples to evaluate

        Returns:
            Dictionary with detailed evaluation results
        """
        # Run baseline evaluation
        baseline_run = self.client.evals.runs.create(
            name=f"Multi-Layer Baseline - {baseline_model}",
            eval_id=eval_id,
            data_source={
                "type": "responses",
                "source": {"type": "responses", "limit": data_limit},
            },
        )

        # Run test evaluation
        test_run = self.client.evals.runs.create(
            name=f"Multi-Layer Test - {test_model}",
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
            "comparison_url": f"https://platform.openai.com/evals/compare/{baseline_run.id}/{test_run.id}",
            "evaluation_type": "multi_layer",
            "baseline_model": baseline_model,
            "test_model": test_model,
            "data_limit": data_limit
        }

    def evaluate_from_logs(
        self,
        eval_id: str,
        days_back: int = 7,
        model_filter: Optional[str] = None
    ) -> str:
        """
        Evaluate agent performance from historical logs with multi-layer analysis

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
            name=f"Multi-Layer Historical Evaluation - {days_back} days",
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
