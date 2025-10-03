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
        # Find the last END_CALL marker using rfind
        end_pos = text.rfind(self.END_CALL)
        if end_pos == -1:
            raise ValueError("No END_CALL marker found")
        
        # Find the last BEGIN_CALL before the END_CALL
        begin_pos = text.rfind(self.BEGIN_CALL, 0, end_pos)
        if begin_pos == -1:
            raise ValueError("No BEGIN_CALL marker found before END_CALL")
        
        # Extract thought (everything before BEGIN_CALL)
        thought = text[:begin_pos].strip()
        
        # Extract function call content (between BEGIN_CALL and END_CALL)
        call_content = text[begin_pos + len(self.BEGIN_CALL):end_pos].strip()
        
        if not call_content:
            raise ValueError("Empty function call content")
        
        # Split by ARG_SEP to get function name and arguments
        parts = call_content.split(self.ARG_SEP)
        
        if len(parts) < 1:
            raise ValueError("No function name found")
        
        function_name = parts[0].strip()
        if not function_name:
            raise ValueError("Empty function name")
        
        # Parse arguments (pairs of name, value)
        arguments = {}
        # Process each part after the function name
        for i in range(1, len(parts)):
            arg_part = parts[i].strip()
            if not arg_part:
                continue
                
            # Split by newlines to separate arg name and value
            lines = [line.strip() for line in arg_part.split('\n') if line.strip()]
            
            if len(lines) >= 2:
                arg_name = lines[0]
                arg_value = '\n'.join(lines[1:])  # Join remaining lines as value (handles multiline)
                arguments[arg_name] = arg_value
            elif len(lines) == 1:
                # Edge case: might be just the arg name, value could be empty
                arguments[lines[0]] = ""
            # If len(lines) == 0, skip this part
        
        return {
            "thought": thought,
            "name": function_name,
            "arguments": arguments
        }
