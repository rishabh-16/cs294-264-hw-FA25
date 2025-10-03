#!/usr/bin/env python3
"""
Quick test script to manually test the agent with a simple task.
"""

import os
from agent import ReactAgent
from llm import OpenAIModel
from response_parser import ResponseParser
from envs import DumbEnvironment

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("Testing CS294 ReAct Agent with a simple task...")
    
    # Initialize components
    llm = OpenAIModel("----END_FUNCTION_CALL----", "gpt-4o-mini")
    parser = ResponseParser()
    agent = ReactAgent("test-agent", parser, llm)
    
    # Add environment functions
    env = DumbEnvironment()
    
    # Create a wrapper function for DumbEnvironment
    def run_bash_cmd(command: str) -> str:
        """Run a bash command using DumbEnvironment"""
        return env.execute(command)
    
    # Add functions to agent
    agent.add_functions([run_bash_cmd, agent.add_instructions_and_backtrack])
    
    # Simple test task
    task = "Use the run_bash_cmd function to list the files in the current directory, then finish with a summary of what you found."
    
    print(f"Task: {task}")
    print("\nRunning agent...")
    
    try:
        result = agent.run(task, max_steps=5)
        print(f"\nAgent completed successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"\nError running agent: {e}")

if __name__ == "__main__":
    main()
