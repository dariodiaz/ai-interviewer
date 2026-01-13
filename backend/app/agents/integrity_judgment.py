"""Integrity Judgment Agent - optional per-message integrity assessment."""
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.llm_factory import get_llm
from app.agents.prompts import INTEGRITY_JUDGMENT_PROMPT
from app.schemas.interview import IntegrityAssessment


class IntegrityJudgmentAgent:
    """Agent for assessing potential integrity issues in answers."""

    def __init__(self):
        """Initialize the integrity judgment agent."""
        self.llm = get_llm(temperature=0.0)  # Deterministic for fairness
        self.parser = PydanticOutputParser(pydantic_object=IntegrityAssessment)

    def assess(
        self,
        question: str,
        answer: str,
        response_time_ms: int,
        paste_detected: bool,
        previous_answers: list[str],
    ) -> IntegrityAssessment:
        """
        Assess potential integrity issues in an answer.

        Args:
            question: The question asked
            answer: The candidate's answer
            response_time_ms: Response time in milliseconds
            paste_detected: Whether paste was detected
            previous_answers: Previous answers for style comparison

        Returns:
            IntegrityAssessment with certainty and indicators
        """
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are analyzing interview integrity."),
                (
                    "human",
                    INTEGRITY_JUDGMENT_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your assessment:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        # Format previous answers
        previous_answers_str = "\n\n".join(
            [f"Answer {i+1}: {ans}" for i, ans in enumerate(previous_answers[-3:])]
        ) or "No previous answers yet"

        # Execute assessment
        result = chain.invoke(
            {
                "question": question,
                "answer": answer,
                "response_time_ms": response_time_ms,
                "paste_detected": paste_detected,
                "previous_answers": previous_answers_str,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )

        return result


# Convenience function
def assess_integrity(
    question: str,
    answer: str,
    response_time_ms: int = 0,
    paste_detected: bool = False,
    previous_answers: list[str] | None = None,
) -> IntegrityAssessment:
    """
    Assess integrity of an answer.

    Args:
        question: Question asked
        answer: Candidate's answer
        response_time_ms: Response time
        paste_detected: Paste detection flag
        previous_answers: Previous answers for comparison

    Returns:
        IntegrityAssessment object
    """
    agent = IntegrityJudgmentAgent()
    return agent.assess(
        question, answer, response_time_ms, paste_detected, previous_answers or []
    )
