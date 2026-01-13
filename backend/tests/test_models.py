"""Basic tests for database models."""
import pytest
from app.models import Interview, Message
from app.utils.state_machine import InterviewStatus, InterviewStateMachine, StateTransitionError


def test_interview_creation():
    """Test creating an interview instance."""
    interview = Interview(
        status=InterviewStatus.DRAFT.value,
        target_questions=8,
        difficulty_start=5,
    )
    assert interview.status == InterviewStatus.DRAFT.value
    assert interview.target_questions == 8
    assert interview.difficulty_start == 5


def test_state_machine_valid_transitions():
    """Test valid state transitions."""
    # DRAFT -> READY
    assert InterviewStateMachine.can_transition(
        InterviewStatus.DRAFT, InterviewStatus.READY
    )
    
    # READY -> ASSIGNED
    assert InterviewStateMachine.can_transition(
        InterviewStatus.READY, InterviewStatus.ASSIGNED
    )
    
    # ASSIGNED -> IN_PROGRESS
    assert InterviewStateMachine.can_transition(
        InterviewStatus.ASSIGNED, InterviewStatus.IN_PROGRESS
    )
    
    # IN_PROGRESS -> COMPLETED
    assert InterviewStateMachine.can_transition(
        InterviewStatus.IN_PROGRESS, InterviewStatus.COMPLETED
    )


def test_state_machine_invalid_transitions():
    """Test invalid state transitions."""
    # DRAFT -> COMPLETED (skipping states)
    assert not InterviewStateMachine.can_transition(
        InterviewStatus.DRAFT, InterviewStatus.COMPLETED
    )
    
    # COMPLETED -> anything (terminal state)
    assert not InterviewStateMachine.can_transition(
        InterviewStatus.COMPLETED, InterviewStatus.DRAFT
    )
    
    # READY -> DRAFT (backwards)
    assert not InterviewStateMachine.can_transition(
        InterviewStatus.READY, InterviewStatus.DRAFT
    )


def test_state_machine_preconditions():
    """Test state transition preconditions."""
    interview = Interview(
        status=InterviewStatus.DRAFT.value,
        target_questions=8,
        difficulty_start=5,
    )
    
    # Should fail: no match_analysis_json
    with pytest.raises(StateTransitionError):
        InterviewStateMachine.validate_transition(interview, InterviewStatus.READY)
    
    # Add match_analysis_json
    interview.match_analysis_json = {
        "match_score": 8,
        "match_summary": "Good fit",
        "focus_areas": ["Python", "FastAPI", "SQL"]
    }
    
    # Should succeed now
    InterviewStateMachine.validate_transition(interview, InterviewStatus.READY)


def test_message_creation():
    """Test creating a message instance."""
    message = Message(
        interview_id=1,
        role="assistant",
        content="Hello, let's begin the interview.",
        question_number=1,
        difficulty_level=5.0,
    )
    assert message.role == "assistant"
    assert message.content == "Hello, let's begin the interview."
    assert message.question_number == 1
    assert message.difficulty_level == 5.0
