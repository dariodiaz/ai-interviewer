"""Agents package - LangChain agents for interview orchestration."""
from app.agents.answer_evaluation import AnswerEvaluationAgent, evaluate_answer
from app.agents.document_analysis import DocumentAnalysisAgent, analyze_documents
from app.agents.integrity_judgment import IntegrityJudgmentAgent, assess_integrity
from app.agents.interview_introduction import (
    generate_introduction,
    generate_closing_message,
)
from app.agents.message_classification import MessageClassificationAgent, classify_message
from app.agents.question_generation import QuestionGenerationAgent, generate_question
from app.agents.report_generation import ReportGenerationAgent, generate_report

__all__ = [
    # Agent classes
    "DocumentAnalysisAgent",
    "AnswerEvaluationAgent",
    "QuestionGenerationAgent",
    "MessageClassificationAgent",
    "ReportGenerationAgent",
    "IntegrityJudgmentAgent",
    # Convenience functions
    "analyze_documents",
    "evaluate_answer",
    "generate_question",
    "classify_message",
    "generate_report",
    "assess_integrity",
    # Template functions
    "generate_introduction",
    "generate_closing_message",
]
