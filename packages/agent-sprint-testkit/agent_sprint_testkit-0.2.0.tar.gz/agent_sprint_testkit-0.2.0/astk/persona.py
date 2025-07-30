"""
Synthetic persona generation for agent testing
"""

from typing import List, Optional
import asyncio
from deepeval import Synthesizer
from .schema import PersonaConfig


class PersonaGenerator:
    """Generates synthetic personas for agent testing"""

    def __init__(self):
        self.synthesizer = Synthesizer()

    async def generate_conversations(
        self,
        config: PersonaConfig,
        n_conversations: int = 50,
        max_turns: int = 5
    ) -> List[List[dict]]:
        """
        Generate synthetic conversations based on persona config

        Args:
            config: Persona configuration
            n_conversations: Number of conversations to generate
            max_turns: Maximum conversation turns

        Returns:
            List of conversations, where each conversation is a list of message dicts
        """
        # Configure synthesizer with persona traits
        traits = config.traits or []
        base_prompt = f"You are an {config.archetype}. " + \
            f"Your traits include: {', '.join(traits)}" if traits else ""

        conversations = []
        for _ in range(n_conversations):
            messages = []

            # Generate initial user message
            user_msg = await self.synthesizer.generate(
                persona=config.archetype,
                temperature=config.temperature,
                prompt=base_prompt
            )
            messages.append({"role": "user", "content": user_msg})

            # Generate subsequent turns
            for _ in range(max_turns - 1):
                # Simulate agent response (placeholder)
                agent_msg = "Placeholder agent response"
                messages.append({"role": "assistant", "content": agent_msg})

                # Generate user follow-up
                user_msg = await self.synthesizer.generate(
                    persona=config.archetype,
                    temperature=config.temperature,
                    prompt=base_prompt,
                    conversation_history=messages
                )
                messages.append({"role": "user", "content": user_msg})

            conversations.append(messages)

        return conversations

    @classmethod
    async def create_conversations(
        cls,
        config: PersonaConfig,
        n_conversations: int = 50,
        max_turns: int = 5
    ) -> List[List[dict]]:
        """Factory method to create generator and generate conversations"""
        generator = cls()
        return await generator.generate_conversations(
            config,
            n_conversations=n_conversations,
            max_turns=max_turns
        )
