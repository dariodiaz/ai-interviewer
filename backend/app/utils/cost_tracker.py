"""Cost tracking utility for LLM API usage."""
from typing import Dict, Optional
import tiktoken


# Pricing per 1K tokens (USD) - Updated Jan 2024
PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "gemini-pro": {"input": 0.00025, "output": 0.0005},
    "gemini-2.5-flash": {"input": 0.000075, "output": 0.00015},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
}


class CostTracker:
    """Track LLM API costs and token usage."""

    @staticmethod
    def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Estimate token count for text.

        For OpenAI models, uses tiktoken for accurate counting.
        For Gemini models, uses character-based estimation.

        Args:
            text: Text to count tokens for
            model: Model name

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        # For OpenAI models, use tiktoken
        if model.startswith("gpt"):
            try:
                encoding = tiktoken.encoding_for_model(model)
                return len(encoding.encode(text))
            except Exception:
                # Fallback to cl100k_base encoding
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text))

        # For Gemini models, estimate based on characters
        # Gemini uses approximately 1 token per 4 characters
        return len(text) // 4

    @staticmethod
    def calculate_cost(
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> float:
        """
        Calculate cost for LLM API call.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model name

        Returns:
            Estimated cost in USD
        """
        # Get pricing for model (use closest match)
        pricing = None
        for model_key in PRICING:
            if model.startswith(model_key):
                pricing = PRICING[model_key]
                break

        if not pricing:
            # Default to gemini-pro pricing if model not found
            pricing = PRICING["gemini-pro"]

        # Calculate cost (pricing is per 1K tokens)
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    @staticmethod
    def get_token_counts(
        prompt: str,
        response: str,
        model: str,
        actual_counts: Optional[Dict[str, int]] = None,
    ) -> Dict[str, int]:
        """
        Get token counts for prompt and response.

        Uses actual counts if provided (from OpenAI), otherwise estimates.

        Args:
            prompt: Input prompt
            response: Model response
            model: Model name
            actual_counts: Optional actual token counts from API

        Returns:
            Dictionary with prompt_tokens, completion_tokens, total_tokens
        """
        if actual_counts:
            return {
                "prompt_tokens": actual_counts.get("prompt_tokens", 0),
                "completion_tokens": actual_counts.get("completion_tokens", 0),
                "total_tokens": actual_counts.get("total_tokens", 0),
            }

        # Estimate tokens
        prompt_tokens = CostTracker.estimate_tokens(prompt, model)
        completion_tokens = CostTracker.estimate_tokens(response, model)

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
