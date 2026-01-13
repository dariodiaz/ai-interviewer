"""Answer Evaluation Agent - scores and evaluates candidate answers."""
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.llm_factory import get_llm
from app.agents.prompts import ANSWER_EVALUATION_PROMPT
from app.schemas.message import AnswerEvaluation


class AnswerEvaluationAgent:
    """Agent for evaluating candidate answers."""

    def __init__(self):
        """Initialize the answer evaluation agent."""
        self.llm = get_llm(temperature=0.0)  # Deterministic for fairness
        self.parser = PydanticOutputParser(pydantic_object=AnswerEvaluation)

    def evaluate(self, question: str, answer: str) -> AnswerEvaluation:
        """
        Evaluate a candidate's answer to a question.

        Args:
            question: The question that was asked
            answer: The candidate's answer

        Returns:
            AnswerEvaluation with score, rationale, evidence, and followup hint
        """
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert technical interviewer."),
                (
                    "human",
                    ANSWER_EVALUATION_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your evaluation:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        # Execute the evaluation
        result = chain.invoke(
            {
                "question": question,
                "answer": answer,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )

        return result


# Convenience function
def evaluate_answer(question: str, answer: str) -> AnswerEvaluation:
    """
    Evaluate a candidate's answer.

    Args:
        question: The question asked
        answer: The candidate's answer

    Returns:
        AnswerEvaluation object
    """
    agent = AnswerEvaluationAgent()
    return agent.evaluate(question, answer)
