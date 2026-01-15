"""Base agent class with error handling and retry logic."""
import logging
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.exceptions import OutputParserException

from app.config import settings
from app.utils.llm_cache import get_cache
from app.utils.cost_tracker import CostTracker
from app.models.llm_usage import LLMUsage

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
        self.cache = get_cache() if settings.cache_enabled else None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMInvocationError, OutputParserException)),
    )
    def invoke_with_retry(
        self,
        chain: Any,
        inputs: dict,
        model: Optional[str] = None,
        temperature: float = 0.0,
        use_cache: bool = True,
    ) -> Any:
        """
        Invoke a LangChain chain with automatic retry (synchronous version).
        
        This is the backward-compatible synchronous version.
        Cost tracking is disabled for sync calls.

        Args:
            chain: The LangChain chain to invoke
            inputs: Input dictionary for the chain
            model: Model name (optional, for logging)
            temperature: Temperature setting
            use_cache: Whether to use caching (default: True)

        Returns:
            Chain output

        Raises:
            LLMInvocationError: If all retries fail
        """
        # Generate cache key from inputs
        prompt_str = str(inputs)
        cache_key = None
        cached_response = None

        if self.cache and use_cache and model:
            cache_key = self.cache.generate_key(
                prompt=prompt_str,
                model=model,
                temperature=temperature,
                agent_name=self.agent_name,
            )
            cached_response = self.cache.get(cache_key)

        if cached_response:
            self.logger.info(f"{self.agent_name} agent - Cache HIT")
            return cached_response

        try:
            self.logger.info(f"Invoking {self.agent_name} agent - Cache MISS")
            self.logger.debug(f"Inputs: {inputs}")

            result = chain.invoke(inputs)

            self.logger.info(f"{self.agent_name} agent completed successfully")
            self.logger.debug(f"Output: {result}")

            # Cache the response
            if self.cache and use_cache and cache_key:
                result_str = str(result)
                self.cache.set(cache_key, result_str)
                self.logger.debug(f"Cached response with key: {cache_key[:16]}...")

            return result

        except OutputParserException as e:
            self.logger.error(f"Output parsing failed: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{self.agent_name} agent failed: {e}")
            raise LLMInvocationError(f"Failed to invoke {self.agent_name}: {str(e)}") from e

    async def invoke_with_retry_async(
        self,
        chain: Any,
        inputs: dict,
        model: str,
        temperature: float = 0.0,
        use_cache: bool = True,
        db: Optional[AsyncSession] = None,
        interview_id: Optional[int] = None,
    ) -> Any:
        """
        Invoke a LangChain chain with automatic retry, caching, and cost tracking (async version).

        Args:
            chain: The LangChain chain to invoke
            inputs: Input dictionary for the chain
            model: Model name for cost tracking
            temperature: Temperature setting
            use_cache: Whether to use caching (default: True)
            db: Database session for cost tracking
            interview_id: Interview ID for cost tracking

        Returns:
            Chain output

        Raises:
            LLMInvocationError: If all retries fail
        """
        # Generate cache key from inputs
        prompt_str = str(inputs)
        cache_key = None
        cached_response = None

        if self.cache and use_cache:
            cache_key = self.cache.generate_key(
                prompt=prompt_str,
                model=model,
                temperature=temperature,
                agent_name=self.agent_name,
            )
            cached_response = self.cache.get(cache_key)

        if cached_response:
            self.logger.info(f"{self.agent_name} agent - Cache HIT")
            
            # Track cache hit in database if enabled
            if settings.cost_tracking_enabled and db and interview_id:
                await self._track_usage(
                    db=db,
                    interview_id=interview_id,
                    model=model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    cost=0.0,
                    cached=True,
                )
            
            return cached_response

        try:
            self.logger.info(f"Invoking {self.agent_name} agent - Cache MISS")
            self.logger.debug(f"Inputs: {inputs}")

            result = chain.invoke(inputs)

            self.logger.info(f"{self.agent_name} agent completed successfully")
            self.logger.debug(f"Output: {result}")

            # Cache the response
            if self.cache and use_cache and cache_key:
                # Convert result to string for caching
                result_str = str(result)
                self.cache.set(cache_key, result_str)
                self.logger.debug(f"Cached response with key: {cache_key[:16]}...")

            # Track cost if enabled
            if settings.cost_tracking_enabled and db and interview_id:
                await self._track_cost(
                    db=db,
                    interview_id=interview_id,
                    model=model,
                    prompt=prompt_str,
                    response=str(result),
                )

            return result

        except OutputParserException as e:
            self.logger.error(f"Output parsing failed: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{self.agent_name} agent failed: {e}")
            raise LLMInvocationError(f"Failed to invoke {self.agent_name}: {str(e)}") from e

    async def _track_cost(
        self,
        db: AsyncSession,
        interview_id: int,
        model: str,
        prompt: str,
        response: str,
    ) -> None:
        """
        Track LLM usage cost in database.

        Args:
            db: Database session
            interview_id: Interview ID
            model: Model name
            prompt: Input prompt
            response: Model response
        """
        try:
            # Get token counts
            token_counts = CostTracker.get_token_counts(
                prompt=prompt,
                response=response,
                model=model,
            )

            # Calculate cost
            cost = CostTracker.calculate_cost(
                prompt_tokens=token_counts["prompt_tokens"],
                completion_tokens=token_counts["completion_tokens"],
                model=model,
            )

            await self._track_usage(
                db=db,
                interview_id=interview_id,
                model=model,
                prompt_tokens=token_counts["prompt_tokens"],
                completion_tokens=token_counts["completion_tokens"],
                cost=cost,
                cached=False,
            )

            self.logger.info(
                f"Cost tracked - Tokens: {token_counts['total_tokens']}, "
                f"Cost: ${cost:.6f}"
            )

        except Exception as e:
            self.logger.error(f"Failed to track cost: {e}")
            # Don't fail the request if cost tracking fails

    async def _track_usage(
        self,
        db: AsyncSession,
        interview_id: int,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
        cached: bool,
    ) -> None:
        """
        Save LLM usage to database.

        Args:
            db: Database session
            interview_id: Interview ID
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost: Estimated cost
            cached: Whether response was cached
        """
        try:
            usage = LLMUsage(
                interview_id=interview_id,
                agent_name=self.agent_name,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost=cost,
                cached=cached,
            )
            db.add(usage)
            await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to save usage to database: {e}")
            await db.rollback()

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
