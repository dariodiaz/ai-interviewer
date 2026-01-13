"""Report Generation Agent - creates final interview reports."""
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.llm_factory import get_llm
from app.agents.prompts import REPORT_GENERATION_PROMPT
from app.schemas.interview import FinalReport


class ReportGenerationAgent:
    """Agent for generating final interview reports."""

    def __init__(self):
        """Initialize the report generation agent."""
        self.llm = get_llm(temperature=0.0)  # Deterministic for consistency
        self.parser = PydanticOutputParser(pydantic_object=FinalReport)

    def generate_report(
        self,
        match_analysis: dict,
        transcript: str,
        question_scores: list[dict],
        telemetry_summary: str,
    ) -> FinalReport:
        """
        Generate a final interview report.

        Args:
            match_analysis: Initial match analysis results
            transcript: Full interview transcript
            question_scores: List of per-question scores and evaluations
            telemetry_summary: Summary of telemetry data (paste events, response times)

        Returns:
            FinalReport with score, summary, gaps, and integrity flags
        """
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert technical recruiter creating interview reports."),
                (
                    "human",
                    REPORT_GENERATION_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your report:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        # Format the data
        match_analysis_str = (
            f"Match Score: {match_analysis.get('match_score')}/10\n"
            f"Summary: {match_analysis.get('match_summary')}\n"
            f"Focus Areas: {', '.join(match_analysis.get('focus_areas', []))}"
        )

        question_scores_str = "\n".join(
            [
                f"Q{i+1}: Score {score.get('score', 'N/A')}/10 - {score.get('rationale', 'N/A')}"
                for i, score in enumerate(question_scores)
            ]
        )

        # Execute report generation
        result = chain.invoke(
            {
                "match_analysis": match_analysis_str,
                "transcript": transcript,
                "question_scores": question_scores_str,
                "telemetry_summary": telemetry_summary,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )

        return result


# Convenience function
def generate_report(
    match_analysis: dict,
    transcript: str,
    question_scores: list[dict],
    telemetry_summary: str = "",
) -> FinalReport:
    """
    Generate final interview report.

    Args:
        match_analysis: Match analysis data
        transcript: Full transcript
        question_scores: Per-question scores
        telemetry_summary: Telemetry summary

    Returns:
        FinalReport object
    """
    agent = ReportGenerationAgent()
    return agent.generate_report(match_analysis, transcript, question_scores, telemetry_summary)
