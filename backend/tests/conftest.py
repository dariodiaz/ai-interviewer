"""Test configuration."""
import pytest


@pytest.fixture
def sample_interview_data():
    """Sample interview data for testing."""
    return {
        "status": "DRAFT",
        "target_questions": 8,
        "difficulty_start": 5,
    }


@pytest.fixture
def sample_match_analysis():
    """Sample match analysis data."""
    return {
        "match_score": 8,
        "match_summary": "Strong candidate with relevant experience",
        "focus_areas": ["Python", "FastAPI", "Database Design", "Testing", "LangChain"],
    }
