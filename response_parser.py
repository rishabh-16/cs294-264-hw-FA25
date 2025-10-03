class ResponseParser:
    """
    Parses LLM responses to extract a single function call using a rigid textual format.

    The LLM must output exactly one function call at the end of its response.
    Do NOT use JSON or XML. Use rfind to locate the final markers.
    """

    BEGIN_CALL = "----BEGIN_FUNCTION_CALL----"
    END_CALL = "----END_FUNCTION_CALL----"
    ARG_SEP = "----ARG----"

    # Students should include this exact template in the system prompt so the LLM follows it.
    response_format = f"""
your_thoughts_here
...
{BEGIN_CALL}
function_name
{ARG_SEP}
arg1_name
arg1_value (can be multiline)
{ARG_SEP}
arg2_name
arg2_value (can be multiline)
...
{END_CALL}
"""

    def parse(self, text: str) -> dict:
        """
        Parse the function call from `text` using string.rfind to avoid confusion with
        earlier delimiter-like content in the reasoning.

        Returns a dictionary: {"thought": str, "name": str, "arguments": dict}
        """
        # Find the last occurrence of END_CALL
        end_call_pos = text.rfind(self.END_CALL)
        if end_call_pos == -1:
            raise ValueError(f"No {self.END_CALL} found in response")
        
        # Find the last occurrence of BEGIN_CALL before END_CALL
        begin_call_pos = text.rfind(self.BEGIN_CALL, 0, end_call_pos)
        if begin_call_pos == -1:
            raise ValueError(f"No {self.BEGIN_CALL} found before {self.END_CALL}")
        
        # Extract the thought (everything before BEGIN_CALL)
        thought = text[:begin_call_pos].strip()
        
        # Extract the function call content (between BEGIN_CALL and END_CALL)
        call_start = begin_call_pos + len(self.BEGIN_CALL)
        call_content = text[call_start:end_call_pos].strip()
        
        if not call_content:
            raise ValueError("Empty function call content")
        
        # Split by ARG_SEP to get function name and arguments
        parts = call_content.split(self.ARG_SEP)
        
        # First part is the function name
        function_name = parts[0].strip()
        if not function_name:
            raise ValueError("Empty function name")
        
        # Parse arguments from remaining parts
        arguments = {}
        
        # Arguments come in pairs: arg_name, arg_value
        if len(parts) > 1:
            arg_parts = parts[1:]  # Skip function name
            
            # Arguments are structured as: ARG_SEP + arg_name + ARG_SEP + arg_value + ...
            # But since we split by ARG_SEP, we get: [arg_name, arg_value, arg_name, arg_value, ...]
            if len(arg_parts) % 2 != 0:
                raise ValueError("Arguments must come in name-value pairs")
            
            for i in range(0, len(arg_parts), 2):
                if i + 1 >= len(arg_parts):
                    break
                    
                arg_name = arg_parts[i].strip()
                arg_value = arg_parts[i + 1].strip()
                
                if not arg_name:
                    raise ValueError(f"Empty argument name at position {i}")
                
                arguments[arg_name] = arg_value
        
        return {
            "thought": thought,
            "name": function_name,
            "arguments": arguments
        }
