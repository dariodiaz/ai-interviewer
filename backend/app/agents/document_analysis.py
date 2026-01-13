"""Document Analysis Agent - analyzes resume, role description, and job offering."""
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.base import BaseAgent
from app.agents.llm_factory import get_llm
from app.agents.prompts import DOCUMENT_ANALYSIS_PROMPT
from app.agents.validators import DocumentInput
from app.schemas.interview import MatchAnalysis


class DocumentAnalysisAgent(BaseAgent):
    """Agent for analyzing candidate-role fit."""

    def __init__(self):
        """Initialize the document analysis agent."""
        super().__init__("document_analysis")
        self.llm = get_llm(temperature=0.0)  # Deterministic for consistency
        self.parser = PydanticOutputParser(pydantic_object=MatchAnalysis)

    def analyze(
        self, resume_text: str, role_description_text: str, job_offering_text: str
    ) -> MatchAnalysis:
        """
        Analyze the match between candidate and role.

        Args:
            resume_text: Extracted text from candidate's resume
            role_description_text: Extracted text from role description
            job_offering_text: Extracted text from job offering

        Returns:
            MatchAnalysis with score, summary, and focus areas

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        validated = DocumentInput(
            resume_text=resume_text,
            role_description_text=role_description_text,
            job_offering_text=job_offering_text,
        )

        # Create the prompt with format instructions
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert technical recruiter."),
                (
                    "human",
                    DOCUMENT_ANALYSIS_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your analysis:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        # Execute the analysis with retry logic
        result = self.invoke_with_retry(
            chain,
            {
                "resume_text": validated.resume_text,
                "role_description_text": validated.role_description_text,
                "job_offering_text": validated.job_offering_text,
                "format_instructions": self.parser.get_format_instructions(),
            },
        )

        return result


# Convenience function
def analyze_documents(
    resume_text: str, role_description_text: str, job_offering_text: str
) -> MatchAnalysis:
    """
    Analyze candidate-role match.

    Args:
        resume_text: Resume content
        role_description_text: Role description content
        job_offering_text: Job offering content

    Returns:
        MatchAnalysis object
    """
    agent = DocumentAnalysisAgent()
    return agent.analyze(resume_text, role_description_text, job_offering_text)
