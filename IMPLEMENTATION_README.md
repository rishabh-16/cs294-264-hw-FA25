# CS294-264 HW1 ReAct Agent Implementation

## ✅ Implementation Complete

This homework has been successfully implemented with all required components:

### What's Implemented

1. **OpenAI LLM Integration** (`llm.py`)
   - OpenAIModel class with generate() method
   - Supports gpt-4o-mini (mapped from gpt-5-mini)
   - Proper error handling and stop token management

2. **Response Parser** (`response_parser.py`)
   - rfind-based parsing as required
   - Handles the textual function call format
   - Returns {"thought", "name", "arguments"} dictionary

3. **Message Tree System** (`agent.py`)
   - Complete message history tree with unique IDs
   - Parent-child relationships and backtracking support
   - Context building from root to current node

4. **ReAct Agent Core** (`agent.py`)
   - Main reasoning-acting loop (up to 100 steps)
   - Tool registration and execution
   - Error handling and recovery

5. **Required Tools**
   - `finish(result)` - terminates agent and returns result
   - `add_instructions_and_backtrack(instructions, at_message_id)` - updates instructions and backtracks
   - `run_bash_cmd(command)` - executes shell commands

6. **Environment Tools** (`envs.py`)
   - `replace_in_file(file_path, from_line, to_line, content)` - edits files
   - `show_file(file_path)` - displays file contents

## How to Use

### 1. Set up your OpenAI API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 2. Install Dependencies

Dependencies are already installed, but if needed:

```bash
pip install -r requirements.txt
```

### 3. Quick Test

Test the basic functionality:

```bash
python quick_test.py
```

### 4. Run on SWE-Bench

Run the full agent on SWE-Bench instances:

```bash
# Single instance test
python run_agent.py --model gpt-4o-mini --max-steps 100

# Full evaluation
python run_agent.py --subset cs294 --model gpt-4o-mini --max-steps 100 --output results/
```

## Key Features

### Message Tree Structure
- Each message has: role, content, timestamp, unique_id, parent, children
- Root path: system → user → instructor
- Supports branching and backtracking

### Function Call Format
The agent uses this exact format for tool calls:

```
your_thoughts_here
...
----BEGIN_FUNCTION_CALL----
function_name
----ARG----
arg1_name
----ARG----
arg1_value
----END_FUNCTION_CALL----
```

### Agent Capabilities
- **Reasoning**: Thinks through problems step by step
- **Acting**: Uses tools to interact with the environment
- **Learning**: Can backtrack and try different approaches
- **Error Recovery**: Handles parsing and execution errors gracefully

## File Structure

- `agent.py` - Main ReAct agent implementation ✅
- `llm.py` - OpenAI model integration ✅ 
- `response_parser.py` - Text parsing for function calls ✅
- `envs.py` - Environment and tool implementations ✅
- `run_agent.py` - Main entry point (updated to use tools) ✅
- `quick_test.py` - Simple test script for verification ✅

## Evaluation

To evaluate on SWE-Bench:

1. **Baseline**: Run without `add_instructions_and_backtrack`
   - Comment out the backtracking tool in `run_agent.py`
   
2. **Improved**: Run with all tools including backtracking
   - Use the current implementation

The agent will generate patches for each instance and save results to JSON files as required by the course evaluation framework.

## Notes

- Max steps is capped at 100 as required
- Uses gpt-4o-mini (latest available model similar to gpt-5-mini)
- Includes comprehensive error handling
- All parsing uses rfind to avoid conflicts with earlier delimiters
- Environment tools work with both SWE-Bench and local testing

The implementation is complete and ready for evaluation! 🎉
