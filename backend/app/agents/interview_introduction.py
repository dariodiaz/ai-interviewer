"""Interview introduction templates."""


def generate_introduction(
    role_description: str, target_questions: int = 8, expected_duration: int = 30
) -> str:
    """
    Generate a simple interview introduction using a template.

    Args:
        role_description: Description of the role
        target_questions: Number of questions planned
        expected_duration: Expected duration in minutes

    Returns:
        Introduction message
    """
    # Extract role title from description (first line or first 50 chars)
    role_title = role_description.split("\n")[0][:50].strip()

    introduction = f"""Hello! I'm your AI interviewer for today.

I'll be conducting a technical interview for the **{role_title}** position.

**Interview Overview:**
- Number of questions: approximately {target_questions}
- Expected duration: {expected_duration} minutes
- Format: One question at a time

**Rules of Engagement:**
- Please answer each question to the best of your ability
- Feel free to ask for clarification if a question is unclear
- Stay focused on the current question
- Take your time to think through your answers

**Before we begin, do you have any questions about the interview process?**

Once you're ready, let me know and we'll start with the first question!
"""
    return introduction.strip()


def generate_closing_message() -> str:
    """
    Generate a closing message for the interview.

    Returns:
        Closing message
    """
    return """Thank you for completing the interview!

Your responses have been recorded and will be reviewed by our team. We appreciate the time and effort you put into your answers.

You'll hear back from us soon regarding the next steps.

Best of luck!"""
