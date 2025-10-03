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

    def __init__(self, stop_token: str, model_name: str = "gpt-5-mini"):
        # Initialize OpenAI client - gets API key from environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.stop_token = stop_token
        # Fallback to available model if gpt-5-mini isn't available
        if model_name == "gpt-5-mini":
            self.model_name = "gpt-4o-mini"  # Use available model as fallback
        else:
            self.model_name = model_name

    def generate(self, prompt: str) -> str:
        """
        Call the model, obtain text, and ensure the stop token is present.
        Return the raw text including the terminal stop token required by the parser.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for more deterministic responses
                max_tokens=4000,  # Reasonable limit
                stop=[self.stop_token] if self.stop_token else None,
            )
            
            response_text = response.choices[0].message.content
            
            # Ensure the stop token is included in the response
            if self.stop_token and not response_text.endswith(self.stop_token):
                response_text += self.stop_token
                
            return response_text
            
        except Exception as e:
            raise RuntimeError(f"Error generating response from OpenAI: {e}")