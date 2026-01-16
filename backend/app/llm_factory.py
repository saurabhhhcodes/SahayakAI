"""
LLM Factory - Multi-Provider Fallback System
Uses LiteLLM for unified API access to 100+ LLMs
Never runs out of quota - automatically falls back between providers
"""
import os
from typing import Optional, List, Dict
import litellm
from litellm import completion

# Suppress verbose logging
litellm.set_verbose = False

# --- PROVIDER CONFIGURATION ---
# Order matters: First available provider with quota wins

FALLBACK_MODELS = [
    # Tier 1: Groq (Fastest, Free tier has daily limits)
    {
        "model": "groq/llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY",
        "name": "Groq Llama-3.3-70B"
    },
    {
        "model": "groq/llama-3.1-8b-instant", 
        "api_key_env": "GROQ_API_KEY",
        "name": "Groq Llama-3.1-8B"
    },
    # Tier 2: Anthropic Claude (Premium quality)
    {
        "model": "anthropic/claude-3-haiku-20240307",
        "api_key_env": "ANTHROPIC_API_KEY",
        "name": "Anthropic Claude-3-Haiku"
    },
    # Tier 3: OpenRouter (Aggregates many providers)
    {
        # Using a very standard free model identifier
        "model": "openrouter/meta-llama/llama-3-8b-instruct:free", 
        "api_key_env": "OPENROUTER_API_KEY", 
        "name": "OpenRouter Llama-3 (Free)"
    },
    # Tier 4: HuggingFace Inference API (Always available)
    {
        # Using a model guaranteed to be on the free tier inference API
        "model": "huggingface/google/gemma-7b",
        "api_key_env": "HF_TOKEN",
        "name": "HuggingFace Google Gemma-7B"
    },
]


class LLMFactory:
    """
    Multi-provider LLM client with automatic fallback.
    Never fails due to rate limits - cycles through providers.
    """
    
    def __init__(self):
        self.available_models = []
        self._setup_models()
    
    def _setup_models(self):
        """Check which API keys are available and setup models."""
        for model_config in FALLBACK_MODELS:
            api_key = os.environ.get(model_config["api_key_env"])
            if api_key and api_key != "hf_...":  # Skip placeholder keys
                self.available_models.append({
                    "model": model_config["model"],
                    "name": model_config["name"],
                    "api_key": api_key
                })
                print(f"✅ LLM Provider Ready: {model_config['name']}")
        
        if not self.available_models:
            print("⚠️ WARNING: No LLM API keys found. Set GROQ_API_KEY, TOGETHER_API_KEY, or HF_TOKEN.")
    
    def chat(self, messages: List[Dict], system_prompt: str = "", temperature: float = 0.7) -> Dict:
        """
        Send chat completion request with automatic fallback.
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            system_prompt: System instruction to prepend
            temperature: Creativity level (0-1)
        
        Returns:
            Response dict with 'content' and 'model_used' keys
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        last_error = None
        
        for model_info in self.available_models:
            try:
                print(f"🔄 Trying: {model_info['name']}...")
                
                # FORCE JSON for fallback models (smaller models need explicit instruction)
                is_fallback = "groq/llama-3.3-70b" not in model_info["model"] and "claude" not in model_info["model"]
                
                final_messages = list(full_messages) # Copy
                if is_fallback:
                    force_json_msg = {
                        "role": "system", 
                        "content": "CRITICAL INSTRUCTION: You are a JSON-only API. You must return strictly valid JSON matching the defined tool schema. Do not ANY conversational text. Output ONLY the JSON object."
                    }
                    final_messages.append(force_json_msg)

                # Set API key for this provider
                response = completion(
                    model=model_info["model"],
                    messages=final_messages,
                    temperature=temperature if not is_fallback else 0.1, # Lower temp for JSON
                    max_tokens=2048,
                    api_key=model_info["api_key"]
                )
                
                content = response.choices[0].message.content
                print(f"✅ Success: {model_info['name']}")
                
                return {
                    "content": content,
                    "model_used": model_info["name"],
                    "success": True
                }
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Failed: {model_info['name']} - {error_msg[:100]}")
                last_error = error_msg
                
                # Check for rate limit specifically
                if "rate" in error_msg.lower() or "429" in error_msg:
                    print("   ↳ Rate limited, trying next provider...")
                    continue
                elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    print("   ↳ Auth error, trying next provider...")
                    continue
                else:
                    # Unknown error, still try next
                    continue
        
        # All providers failed
        return {
            "content": f"⚠️ All LLM providers exhausted. Last error: {last_error}",
            "model_used": "none",
            "success": False
        }


# Global instance
llm_factory = LLMFactory()


def get_llm_response(user_message: str, system_prompt: str = "", history: List[Dict] = None) -> Dict:
    """
    Convenience function to get LLM response.
    
    Args:
        user_message: The user's input
        system_prompt: System instruction
        history: Previous conversation history
    
    Returns:
        Response dict
    """
    messages = history or []
    messages.append({"role": "user", "content": user_message})
    
    return llm_factory.chat(messages, system_prompt)


if __name__ == "__main__":
    # Test the factory
    print("\n=== LLM Factory Test ===")
    response = get_llm_response(
        "Hello! Tell me a fun fact about teaching.",
        "You are a helpful assistant for teachers."
    )
    print(f"\nResponse from {response['model_used']}:")
    print(response['content'][:500])
