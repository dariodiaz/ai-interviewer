"""Question Generation Agent - generates adaptive interview questions."""
from langchain.prompts import ChatPromptTemplate

from app.agents.llm_factory import get_llm
from app.agents.prompts import QUESTION_GENERATION_PROMPT


class QuestionGenerationAgent:
    """Agent for generating interview questions."""

    def __init__(self):
        """Initialize the question generation agent."""
        self.llm = get_llm(temperature=0.7)  # Some creativity for varied questions

    def generate_question(
        self,
        focus_areas: list[str],
        difficulty_level: float,
        chat_history: str,
        questions_asked: int,
    ) -> str:
        """
        Generate the next interview question.

        Args:
            focus_areas: List of topics to cover in the interview
            difficulty_level: Current difficulty (3-10 scale)
            chat_history: Previous conversation context
            questions_asked: Number of questions already asked

        Returns:
            The next question to ask
        """
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert technical interviewer."),
                ("human", QUESTION_GENERATION_PROMPT),
            ]
        )

        # Create the chain
        chain = prompt | self.llm

        # Execute question generation
        result = chain.invoke(
            {
                "focus_areas": ", ".join(focus_areas),
                "difficulty_level": difficulty_level,
                "chat_history": chat_history or "No previous questions yet.",
                "questions_asked": questions_asked,
            }
        )

        # Extract the text content
        return result.content.strip()


# Convenience function
def generate_question(
    focus_areas: list[str],
    difficulty_level: float,
    chat_history: str = "",
    questions_asked: int = 0,
) -> str:
    """
    Generate the next interview question.

    Args:
        focus_areas: Topics to cover
        difficulty_level: Current difficulty (3-10)
        chat_history: Previous conversation
        questions_asked: Number of questions asked

    Returns:
        Next question string
    """
    agent = QuestionGenerationAgent()
    return agent.generate_question(
        focus_areas, difficulty_level, chat_history, questions_asked
    )
