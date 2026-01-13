"""Message Classification Agent - classifies candidate messages."""
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.llm_factory import get_llm
from app.agents.prompts import MESSAGE_CLASSIFICATION_PROMPT
from app.schemas.interview import MessageClassification


class MessageClassificationAgent:
    """Agent for classifying candidate messages."""

    def __init__(self):
        """Initialize the message classification agent."""
        self.llm = get_llm(temperature=0.0)  # Deterministic for consistency
        self.parser = PydanticOutputParser(pydantic_object=MessageClassification)

    def classify(self, current_question: str, candidate_message: str) -> MessageClassification:
        """
        Classify a candidate's message.

        Args:
            current_question: The current question being asked
            candidate_message: The candidate's message to classify

        Returns:
            MessageClassification with type and confidence
        """
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are analyzing interview messages."),
                (
                    "human",
                    MESSAGE_CLASSIFICATION_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your classification:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        # Execute classification
        result = chain.invoke(
            {
                "current_question": current_question,
                "candidate_message": candidate_message,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )

        return result


# Convenience function
def classify_message(current_question: str, candidate_message: str) -> MessageClassification:
    """
    Classify a candidate's message.

    Args:
        current_question: Current question
        candidate_message: Message to classify

    Returns:
        MessageClassification object
    """
    agent = MessageClassificationAgent()
    return agent.classify(current_question, candidate_message)
