"""
Starter scaffold for the CS 294-264 HW1 ReAct agent.

Students must implement a minimal ReAct agent that:
- Maintains a message history tree (role, content, timestamp, unique_id, parent, children)
- Uses a textual function-call format (see ResponseParser) with rfind-based parsing
- Alternates Reasoning and Acting until calling the tool `finish`
- Supports tools: `run_bash_cmd`, `finish`, and `add_instructions_and_backtrack`

This file intentionally omits core implementations and replaces them with
clear specifications and TODOs.
"""

from typing import List, Callable, Dict, Any
import time

from response_parser import ResponseParser
from llm import LLM, OpenAIModel
import inspect

class ReactAgent:
    """
    Minimal ReAct agent that:
    - Maintains a message history tree with unique ids
    - Builds the LLM context from the root to current node
    - Registers callable tools with auto-generated docstrings in the system prompt
    - Runs a Reason-Act loop until `finish` is called or MAX_STEPS is reached
    """

    def __init__(self, name: str, parser: ResponseParser, llm: LLM):
        self.name: str = name
        self.parser = parser
        self.llm = llm

        # Message tree storage
        self.id_to_message: Dict[int, Dict[str, Any]] = {}
        self.next_id: int = 0
        self.root_message_id: int = -1
        self.current_message_id: int = -1

        # Registered tools
        self.function_map: Dict[str, Callable] = {}

        # Set up the initial structure of the history
        # Create required root nodes and a user node (task) and an instruction node.
        self.system_message_id = self.add_message("system", "You are a Smart ReAct agent.")
        self.user_message_id = self.add_message("user", "")
        self.instructions_message_id = self.add_message("instructor", "")
        
        # NOTE: mandatory finish function that terminates the agent
        self.add_functions([self.finish])

    # -------------------- MESSAGE TREE --------------------
    def add_message(self, role: str, content: str) -> int:
        """
        Create a new message and add it to the tree.

        The message must include fields: role, content, timestamp, unique_id, parent, children.
        Maintain a pointer to the current node and the root node.
        """
        message_id = self.next_id
        self.next_id += 1
        
        # Create the message
        message = {
            "role": role,
            "content": content,
            "timestamp": int(time.time()),
            "unique_id": message_id,
            "parent": self.current_message_id if self.current_message_id != -1 else None,
            "children": []
        }
        
        # Add to storage
        self.id_to_message[message_id] = message
        
        # Link to parent if exists
        if self.current_message_id != -1:
            parent_message = self.id_to_message[self.current_message_id]
            parent_message["children"].append(message_id)
        
        # Update pointers
        if self.root_message_id == -1:
            self.root_message_id = message_id
            
        self.current_message_id = message_id
        
        return message_id

    def set_message_content(self, message_id: int, content: str) -> None:
        """Update message content by id."""
        if message_id not in self.id_to_message:
            raise ValueError(f"Message ID {message_id} not found")
        self.id_to_message[message_id]["content"] = content

    def get_context(self) -> str:
        """
        Build the full LLM context by walking from the root to the current message.
        """
        # Build path from root to current
        path = []
        current_id = self.current_message_id
        
        # Walk backwards to root
        while current_id is not None:
            path.append(current_id)
            message = self.id_to_message[current_id]
            current_id = message["parent"]
        
        # Reverse to get root-to-current path
        path.reverse()
        
        # Build context string
        context_parts = []
        for message_id in path:
            context_parts.append(self.message_id_to_context(message_id))
        
        return "\n".join(context_parts)

    # -------------------- REQUIRED TOOLS --------------------
    def add_functions(self, tools: List[Callable]):
        """
        Add callable tools to the agent's function map.

        The system prompt must include tool descriptions that cover:
        - The signature of each tool
        - The docstring of each tool
        """
        for tool in tools:
            self.function_map[tool.__name__] = tool
        
        # Update system prompt to include tool descriptions
        # The system prompt construction happens in message_id_to_context method
    
    def finish(self, result: str):
        """The agent must call this function with the final result when it has solved the given task. The function calls "git add -A and git diff --cached" to generate a patch and returns the patch as submission.

        Args: 
            result (str); the result generated by the agent

        Returns:
            The result passed as an argument.  The result is then returned by the agent's run method.
        """
        return result 

    def add_instructions_and_backtrack(self, instructions: str, at_message_id: int):
        """
        The agent should call this function if it is making too many mistakes or is stuck.

        The function changes the content of the instruction node with 'instructions' and
        backtracks at the node with id 'at_message_id'. Backtracking means the current node
        pointer moves to the specified node and subsequent context is rebuilt from there.

        Returns a short success string.
        """
        # Update the instruction node content
        self.set_message_content(self.instructions_message_id, instructions)
        
        # Backtrack to the specified message
        if at_message_id not in self.id_to_message:
            raise ValueError(f"Message ID {at_message_id} not found")
        
        self.current_message_id = at_message_id
        
        return f"Successfully updated instructions and backtracked to message {at_message_id}"

    # -------------------- MAIN LOOP --------------------
    def run(self, task: str, max_steps: int) -> str:
        """
        Run the agent's main ReAct loop:
        - Set the user prompt
        - Loop up to max_steps (<= 100):
            - Build context from the message tree
            - Query the LLM
            - Parse a single function call at the end (see ResponseParser)
            - Execute the tool
            - Append tool result to the tree
            - If `finish` is called, return the final result
        """
        # Set the user task content
        self.set_message_content(self.user_message_id, task)
        
        # Ensure we don't exceed max steps
        max_steps = min(max_steps, 100)
        
        for step in range(max_steps):
            try:
                # Build context from message tree
                context = self.get_context()
                
                # Query the LLM
                response = self.llm.generate(context)
                
                # Add assistant response to tree
                self.add_message("assistant", response)
                
                # Parse the function call
                try:
                    parsed = self.parser.parse(response)
                    function_name = parsed["name"]
                    arguments = parsed["arguments"]
                    
                    # Check if function exists
                    if function_name not in self.function_map:
                        error_msg = f"Unknown function: {function_name}"
                        self.add_message("tool", error_msg)
                        continue
                    
                    # Execute the function
                    func = self.function_map[function_name]
                    try:
                        # Call function with arguments
                        if arguments:
                            result = func(**arguments)
                        else:
                            result = func()
                        
                        # Handle finish function specially
                        if function_name == "finish":
                            return str(result)
                        
                        # Add tool result to tree
                        self.add_message("tool", str(result))
                        
                    except Exception as e:
                        error_msg = f"Error executing {function_name}: {str(e)}"
                        self.add_message("tool", error_msg)
                        
                except ValueError as e:
                    # Parser error
                    error_msg = f"Failed to parse function call: {str(e)}"
                    self.add_message("tool", error_msg)
                    
            except Exception as e:
                # LLM error or other unexpected error
                error_msg = f"Unexpected error in step {step}: {str(e)}"
                self.add_message("tool", error_msg)
        
        # Max steps reached without calling finish
        return f"Agent reached maximum steps ({max_steps}) without calling finish"

    def message_id_to_context(self, message_id: int) -> str:
        """
        Helper function to convert a message id to a context string.
        """
        message = self.id_to_message[message_id]
        header = f'----------------------------\n|MESSAGE(role="{message["role"]}", id={message["unique_id"]})|\n'
        content = message["content"]
        if message["role"] == "system":
            tool_descriptions = []
            for tool in self.function_map.values():
                signature = inspect.signature(tool)
                docstring = inspect.getdoc(tool)
                tool_description = f"Function: {tool.__name__}{signature}\n{docstring}\n"
                tool_descriptions.append(tool_description)

            tool_descriptions = "\n".join(tool_descriptions)
            return (
                f"{header}{content}\n"
                f"--- AVAILABLE TOOLS ---\n{tool_descriptions}\n\n"
                f"--- RESPONSE FORMAT ---\n{self.parser.response_format}\n"
            )
        elif message["role"] == "instructor":
            return f"{header}YOU MUST FOLLOW THE FOLLOWING INSTRUCTIONS AT ANY COST. OTHERWISE, YOU WILL BE DECOMISSIONED.\n{content}\n"
        else:
            return f"{header}{content}\n"

def main():
    from envs import DumbEnvironment
    llm = OpenAIModel("----END_FUNCTION_CALL----", "gpt-4o-mini")
    parser = ResponseParser()

    env = DumbEnvironment()
    dumb_agent = ReactAgent("dumb-agent", parser, llm)
    dumb_agent.add_functions([env.run_bash_cmd])
    result = dumb_agent.run("Show the contents of all files in the current directory.", max_steps=10)
    print(result)

if __name__ == "__main__":
    # Optional: students can add their own quick manual test here.
    main()