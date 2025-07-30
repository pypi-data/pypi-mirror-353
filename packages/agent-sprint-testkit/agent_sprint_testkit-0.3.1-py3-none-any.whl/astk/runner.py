"""
Main test runner for executing agent scenarios
"""

import asyncio
import docker
import yaml
from typing import Dict, List, Optional, Union
from pathlib import Path

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .schema import ScenarioConfig
from .persona import PersonaGenerator
from .metrics import QualityMetrics
from .chaos import ChaosMiddleware


class AgentRunner:
    """Executes agent test scenarios"""

    def __init__(
        self,
        agent_entrypoint: Union[str, Path],
        scenario_file: Union[str, Path],
        docker_image: Optional[str] = None
    ):
        self.agent_entrypoint = Path(agent_entrypoint)
        self.scenario_file = Path(scenario_file)
        self.docker_image = docker_image

        # Initialize components
        self.metrics = QualityMetrics()
        self.tracer = trace.get_tracer("astk.runner")

        # Load scenario config
        with open(self.scenario_file) as f:
            config_dict = yaml.safe_load(f)
        self.config = ScenarioConfig(**config_dict)

        # Initialize chaos middleware
        self.chaos = ChaosMiddleware(
            self.config.chaos) if self.config.chaos else None

    async def _start_agent(self) -> None:
        """Start the agent process/container"""
        if self.docker_image:
            # Start agent in Docker
            client = docker.from_env()
            self.container = client.containers.run(
                self.docker_image,
                detach=True,
                remove=True,
                environment={
                    "AGENT_ENTRYPOINT": str(self.agent_entrypoint)
                }
            )
        else:
            # TODO: Start agent as local process
            pass

    async def _stop_agent(self) -> None:
        """Stop the agent process/container"""
        if hasattr(self, "container"):
            self.container.stop()

    async def _send_message(self, message: Dict) -> Dict:
        """
        Send a message to the agent and get response

        Args:
            message: Message to send

        Returns:
            Agent response
        """
        # TODO: Implement actual agent communication
        # This is a placeholder that echoes the message
        await asyncio.sleep(0.1)  # Simulate processing
        return {
            "role": "assistant",
            "content": f"Echo: {message['content']}"
        }

    async def run_conversation(
        self,
        messages: List[Dict]
    ) -> List[Dict]:
        """
        Run a single conversation with the agent

        Args:
            messages: List of conversation messages

        Returns:
            Complete conversation including agent responses
        """
        conversation = []

        with self.tracer.start_as_current_span("conversation") as span:
            try:
                for message in messages:
                    # Process message through chaos middleware
                    if self.chaos:
                        message = await self.chaos.process_request(message)

                    # Send to agent and get response
                    response = await self._send_message(message)

                    conversation.extend([message, response])

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR), str(e))
                raise

        return conversation

    async def run_scenarios(self) -> Dict:
        """
        Run all test scenarios

        Returns:
            Test results summary
        """
        with self.tracer.start_as_current_span("test_run") as span:
            try:
                # Generate synthetic conversations
                conversations = await PersonaGenerator.create_conversations(
                    self.config.persona
                )

                # Start agent
                await self._start_agent()

                results = {
                    "total": len(conversations),
                    "passed": 0,
                    "failed": 0,
                    "conversations": []
                }

                # Run each conversation
                for conv in conversations:
                    conv_result = await self.run_conversation(conv)
                    passed, metrics = self.metrics.evaluate_conversation(
                        conv_result,
                        self.config
                    )

                    results["conversations"].append({
                        "messages": conv_result,
                        "passed": passed,
                        "metrics": metrics
                    })

                    if passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1

                span.set_status(Status(StatusCode.OK))
                return results

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR), str(e))
                raise

            finally:
                await self._stop_agent()

    @classmethod
    async def execute(
        cls,
        agent_entrypoint: Union[str, Path],
        scenario_file: Union[str, Path],
        docker_image: Optional[str] = None
    ) -> Dict:
        """
        Factory method to create runner and execute scenarios

        Args:
            agent_entrypoint: Path to agent entry point
            scenario_file: Path to scenario config file
            docker_image: Optional Docker image to run agent in

        Returns:
            Test results summary
        """
        runner = cls(agent_entrypoint, scenario_file, docker_image)
        return await runner.run_scenarios()
