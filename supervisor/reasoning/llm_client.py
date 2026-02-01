"""
LLM client for AI-powered reasoning.
Supports both Google Gemini and OpenAI GPT models.
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.enabled = os.getenv('LLM_ENABLED', 'false').lower() == 'true'
        
        # Auto-detect provider based on API key format
        if self.api_key.startswith('AIza'):
            self.provider = LLMProvider.GEMINI
            self.model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        elif self.api_key.startswith('sk-'):
            self.provider = LLMProvider.OPENAI
        else:
            self.provider = None
            self.enabled = False
        
        self.client = None
        
        if self.enabled and self.api_key:
            try:
                if self.provider == LLMProvider.GEMINI:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.client = genai.GenerativeModel(self.model)
                elif self.provider == LLMProvider.OPENAI:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: LLM client initialization failed: {e}")
                self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if LLM is enabled and configured."""
        return self.enabled and self.client is not None
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Optional[str]:
        """
        Generate text completion from prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text or None if disabled/error
        """
        if not self.is_enabled():
            return None
        
        try:
            if self.provider == LLMProvider.GEMINI:
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        'temperature': temperature,
                        'max_output_tokens': max_tokens
                    }
                )
                return response.text
            
            elif self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
        except Exception as e:
            print(f"LLM generation error: {e}")
            return None
    
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate with system and user prompts.
        Better for structured tasks.
        """
        if self.provider == LLMProvider.GEMINI:
            # Gemini doesn't have system prompts, combine them
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            return self.generate(full_prompt, temperature=temperature)
        
        elif self.provider == LLMProvider.OPENAI:
            if not self.is_enabled():
                return None
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"LLM generation error: {e}")
                return None
