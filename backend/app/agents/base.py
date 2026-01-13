"""Base agent class with error handling and retry logic."""
import logging
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.exceptions import OutputParserException

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception for agent errors."""

    pass


class LLMInvocationError(AgentError):
    """Error during LLM invocation."""

    pass


class BaseAgent:
    """Base class for all LangChain agents with common functionality."""

    def __init__(self, agent_name: str):
        """
        Initialize base agent.

        Args:
            agent_name: Name of the agent for logging
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agents.{agent_name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMInvocationError, OutputParserException)),
    )
    def invoke_with_retry(self, chain: Any, inputs: dict) -> Any:
        """
        Invoke a LangChain chain with automatic retry on failure.

        Args:
            chain: The LangChain chain to invoke
            inputs: Input dictionary for the chain

        Returns:
            Chain output

        Raises:
            LLMInvocationError: If all retries fail
        """
        try:
            self.logger.info(f"Invoking {self.agent_name} agent")
            self.logger.debug(f"Inputs: {inputs}")

            result = chain.invoke(inputs)

            self.logger.info(f"{self.agent_name} agent completed successfully")
            self.logger.debug(f"Output: {result}")

            return result

        except OutputParserException as e:
            self.logger.error(f"Output parsing failed: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{self.agent_name} agent failed: {e}")
            raise LLMInvocationError(f"Failed to invoke {self.agent_name}: {str(e)}") from e

    def validate_inputs(self, **kwargs: Any) -> None:
        """
        Validate agent inputs.

        Args:
            **kwargs: Input parameters to validate

        Raises:
            ValueError: If validation fails
        """
        for key, value in kwargs.items():
            if value is None:
                raise ValueError(f"{key} cannot be None")

            if isinstance(value, str) and not value.strip():
                raise ValueError(f"{key} cannot be empty")

    def log_cost_estimate(self, input_text: str, output_text: str = "") -> None:
        """
        Log estimated token usage and cost.

        Args:
            input_text: Input text to the LLM
            output_text: Output text from the LLM
        """
        # Rough estimation: 1 token ≈ 4 characters
        input_tokens = len(input_text) // 4
        output_tokens = len(output_text) // 4 if output_text else 0

        self.logger.info(
            f"Estimated tokens - Input: {input_tokens}, Output: {output_tokens}, "
            f"Total: {input_tokens + output_tokens}"
        )
