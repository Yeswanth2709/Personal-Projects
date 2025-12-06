"""
Abstract LLM service with support for multiple providers.
Supports Gemini, OpenAI, and other providers through a unified interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator
import os
from config import (
    LLM_PROVIDER, 
    GEMINI_API_KEY, 
    OPENAI_API_KEY,
    GEMINI_MODEL,
    OPENAI_MODEL,
    TEMPERATURE,
    MAX_TOKENS
)


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""
    
    def __init__(self, temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS):
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate a streaming response from the LLM."""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat with the LLM using a conversation history."""
        pass


class GeminiLLMService(BaseLLMService):
    """Google Gemini LLM service implementation."""
    
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL, **kwargs):
        super().__init__(**kwargs)
        if not api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in .env file.")
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from Gemini."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.model.generate_content(full_prompt)
        return response.text
    
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate a streaming response from Gemini."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.model.generate_content(full_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat with Gemini using conversation history."""
        # Convert messages to Gemini format
        chat = self.model.start_chat(history=[])
        
        # Build conversation
        for i, msg in enumerate(messages[:-1]):  # All but the last message
            if msg["role"] == "user":
                chat.send_message(msg["content"])
        
        # Send final message and get response
        if messages:
            last_message = messages[-1]
            if last_message["role"] == "user":
                response = chat.send_message(last_message["content"])
                return response.text
        
        return ""


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service implementation."""
    
    def __init__(self, api_key: str = OPENAI_API_KEY, model: str = OPENAI_MODEL, **kwargs):
        super().__init__(**kwargs)
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file.")
        
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content
    
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate a streaming response from OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat with OpenAI using conversation history."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content


class LLMServiceFactory:
    """Factory for creating LLM service instances."""
    
    @staticmethod
    def create(provider: str = LLM_PROVIDER, **kwargs) -> BaseLLMService:
        """
        Create an LLM service instance based on the provider.
        
        Args:
            provider: LLM provider name ("gemini", "openai", etc.)
            **kwargs: Additional arguments passed to the service constructor
        
        Returns:
            BaseLLMService instance
        
        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()
        
        if provider == "gemini":
            return GeminiLLMService(**kwargs)
        elif provider == "openai":
            return OpenAILLMService(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Use 'gemini' or 'openai'.")


# Convenience function to get the configured LLM service
def get_llm_service(**kwargs) -> BaseLLMService:
    """Get the configured LLM service instance."""
    return LLMServiceFactory.create(**kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Test the LLM service
    llm = get_llm_service()
    
    # Test generate
    response = llm.generate(
        "What is the capital of France?",
        system_prompt="You are a helpful assistant."
    )
    print("Generate:", response)
    
    # Test chat
    messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi! How can I help you?"},
        {"role": "user", "content": "What is 2+2?"}
    ]
    chat_response = llm.chat(messages)
    print("Chat:", chat_response)
