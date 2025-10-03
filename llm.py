from abc import ABC, abstractmethod
import os
from openai import OpenAI


class LLM(ABC):
    """Abstract base class for Large Language Models."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM given a prompt.
        Must include any required stop-token logic at the caller level.
        """
        raise NotImplementedError


class OpenAIModel(LLM):
    """
    Example LLM implementation using OpenAI's Responses API.

    TODO(student): Implement this class to call your chosen backend (e.g., OpenAI GPT-5 mini)
    and return the model's text output. You should ensure the model produces the response
    format required by ResponseParser and include the stop token in the output string.
    """

    def __init__(self, stop_token: str, model_name: str = "gpt-4o-mini"):
        # Initialize OpenAI client - will use OPENAI_API_KEY from environment
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.stop_token = stop_token
        # Map gpt-5-mini to gpt-4o-mini since gpt-5-mini doesn't exist yet
        if model_name == "gpt-5-mini":
            model_name = "gpt-4o-mini"
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        """
        Call the OpenAI model and return the response.
        Ensures the stop token is present at the end.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stop=[self.stop_token],
                max_tokens=4000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if content is None:
                content = ""
            
            # Ensure the stop token is present at the end
            if not content.endswith(self.stop_token):
                content += self.stop_token
                
            return content
            
        except Exception as e:
            # Return a basic error response with the stop token
            error_response = f"Error calling OpenAI API: {str(e)}\n{self.stop_token}"
            return error_response