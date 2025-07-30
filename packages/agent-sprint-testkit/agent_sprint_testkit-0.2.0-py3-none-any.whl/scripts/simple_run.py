#!/usr/bin/env python3
"""
Simple script to run an agent directly
"""

import asyncio
import sys
import subprocess
import os
from pathlib import Path


async def run_agent(agent_path: Path) -> None:
    """Run the agent directly"""
    print(f"Running agent: {agent_path}")
    print(f"Using Python: {sys.executable}")
    print(f"Python path: {sys.path}")

    # Set up environment to ensure same Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = ':'.join(sys.path)

    try:
        # Run the agent directly
        result = subprocess.run([
            sys.executable, str(agent_path)
        ], capture_output=True, text=True, timeout=30, env=env)

        print("Agent Output:")
        print(result.stdout)

        if result.stderr:
            print("Agent Errors:")
            print(result.stderr)

        if result.returncode != 0:
            print(f"Agent exited with code: {result.returncode}")
        else:
            print("Agent completed successfully!")

    except subprocess.TimeoutExpired:
        print("Agent timed out after 30 seconds")
    except Exception as e:
        print(f"Error running agent: {e}")


def main():
    """Main entry point for console script"""
    if len(sys.argv) < 2:
        print("Usage: astk-run <agent_path>")
        print("Example: astk-run examples/agents/file_qa_agent.py")
        sys.exit(1)

    agent_path = Path(sys.argv[1])
    if not agent_path.exists():
        print(f"Agent file not found: {agent_path}")
        sys.exit(1)

    asyncio.run(run_agent(agent_path))


if __name__ == "__main__":
    main()
