"""
Chaos testing and fault injection for agent evaluation
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from .schema import ChaosConfig


class ChaosController:
    """Controls fault injection and chaos testing"""

    def __init__(self, config: ChaosConfig):
        self.config = config if isinstance(
            config, ChaosConfig) else ChaosConfig(**config)

    async def maybe_inject_latency(self) -> Optional[float]:
        """
        Maybe inject artificial latency based on config

        Returns:
            Injected latency in ms if applied, None otherwise
        """
        if not self.config.inject_latency:
            return None

        latency = random.choice(self.config.inject_latency)
        await asyncio.sleep(latency / 1000.0)  # Convert ms to seconds
        return latency

    def should_drop_tool(self, tool_name: str) -> bool:
        """Check if a tool call should be dropped"""
        if not self.config.drop_tool:
            return False
        return tool_name in self.config.drop_tool

    def maybe_malform_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maybe malform a message based on config

        Args:
            message: Original message dict

        Returns:
            Potentially malformed message dict
        """
        if not self.config.malform_messages:
            return message

        # Randomly select malformation type
        malform_type = random.choice([
            "drop_field",
            "invalid_type",
            "extra_field"
        ])

        message = message.copy()

        if malform_type == "drop_field":
            if "content" in message:
                del message["content"]

        elif malform_type == "invalid_type":
            if "content" in message:
                message["content"] = random.randint(1, 1000)

        elif malform_type == "extra_field":
            message["_invalid_field"] = "".join(
                random.choices("abcdefghijklmnopqrstuvwxyz", k=10)
            )

        return message


class ChaosMiddleware:
    """Middleware for injecting chaos into agent interactions"""

    def __init__(self, config: ChaosConfig):
        self.controller = ChaosController(config)

    async def process_request(
        self,
        request: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming request, potentially injecting faults

        Args:
            request: Original request dict
            context: Optional request context

        Returns:
            Potentially modified request dict
        """
        # Maybe inject latency
        latency = await self.controller.maybe_inject_latency()
        if latency:
            request.setdefault("metadata", {})["injected_latency_ms"] = latency

        # Maybe malform message
        request = self.controller.maybe_malform_message(request)

        return request

    def process_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process a tool call, potentially dropping it

        Args:
            tool_name: Name of tool being called
            args: Tool call arguments

        Returns:
            None if tool call should be dropped, args dict otherwise
        """
        if self.controller.should_drop_tool(tool_name):
            return None
        return args
