from utils import get_sb_environment
import subprocess

class LimitsExceeded(Exception):
    """Raised when the agent has reached its step limit."""


class SWEEnvironment:
    """
    Minimal interface to the SWEBench execution environment.

    Students may use their own wrapper. The environment must expose:
    - execute(command: str) -> str: Run a shell command and return stdout, or raise ValueError on failure
    """

    def __init__(self, instance: dict):
        self.env = get_sb_environment(instance)
     
    # -------------------- REQUIRED TOOLS --------------------
    def run_bash_cmd(self, command: str) -> str:
        """
        Run the command in a bash shell and return the output or throw a ValueError
        if the process returns non-zero exit code.

        Args;
            command (str): the shell command to run

        Returns:
            The output of running the shell command
        """
        try:
            output = self.env.execute(command)
        except subprocess.TimeoutExpired as e:
            output = e.output.decode("utf-8", errors="replace") if e.output else ""
            raise ValueError(output)
        except TimeoutError:
            raise ValueError("TimeoutError")
        return output
    
    def generate_patch(self, result: str) -> str:
        """
        Generate a patch from the result (for SWE-Bench)
        """
        try:
            patch_output = self.env.execute("git add -A && git diff --cached")
            if patch_output.strip():
                return patch_output
            else:
                return f"{result}\n\nNo changes detected to generate a patch."
        except Exception as e:
            return f"{result}\n\nError running git commands: {e}"
    
    # -------------------- TODO(student): add more functions here if you want --------------------
    def replace_in_file(self, file_path: str, from_line: int, to_line: int, content: str) -> str:
        """
        [Optional] Replace the content of the file from the given line to the given line with the given content
        
        Args:
            file_path (str): Path to the file to modify
            from_line (int): Starting line number (1-based)
            to_line (int): Ending line number (1-based, inclusive)
            content (str): New content to replace the lines with
            
        Returns:
            Success message or error description
        """
        try:
            # Read the current file content
            current_content = self.env.execute(f"cat '{file_path}'")
            lines = current_content.split('\n')
            
            # Convert to 0-based indexing and validate
            from_idx = from_line - 1
            to_idx = to_line - 1
            
            if from_idx < 0 or to_idx >= len(lines) or from_idx > to_idx:
                return f"Error: Invalid line range {from_line}-{to_line} for file with {len(lines)} lines"
            
            # Replace the specified lines
            new_lines = lines[:from_idx] + [content] + lines[to_idx + 1:]
            new_content = '\n'.join(new_lines)
            
            # Write the new content to a temporary file and then move it
            temp_file = f"/tmp/temp_edit_{file_path.replace('/', '_')}"
            write_cmd = f"cat > '{temp_file}' << 'EOF'\n{new_content}\nEOF"
            self.env.execute(write_cmd)
            
            # Move temp file to target
            self.env.execute(f"mv '{temp_file}' '{file_path}'")
            
            return f"Successfully replaced lines {from_line}-{to_line} in {file_path}"
            
        except Exception as e:
            return f"Error replacing content in {file_path}: {str(e)}"
    
    def show_file(self, file_path: str) -> str:
        """
        [Optional] Show the content of the file
        
        Args:
            file_path (str): Path to the file to display
            
        Returns:
            File content or error message
        """
        try:
            return self.env.execute(f"cat '{file_path}'")
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"

class DumbEnvironment:
    """
    Dumb environment that just executes the command
    """

    def execute(self, command: str) -> str:
        """
        Run the command in bash and return the output

        Args;
            command (str): the shell command to run

        Returns:
            The output of running the shell command
        """
        result = subprocess.run(command, capture_output=True, shell=True, check=False)
        output = f"--STDOUT--\n{result.stdout.decode()}\n--STDERR--\n{result.stderr.decode()}"
        if result.returncode:
            raise ValueError(output)
        return output