from app.services.workflow import AgentState, generate_question


def test_blank_session_id_is_rejected(client):
    response = client.post(
        "/api/interview",
        json={"sessionId": "   ", "message": "Hello there"},
    )
    assert response.status_code == 422


def test_generate_question_avoids_exact_duplicates():
    state: AgentState = {
        "session_id": "session-dup",
        "candidate_data": {
            "name": "Demo Candidate",
            "jobRole": "Software Engineer",
            "experienceLevel": "Intermediate",
            "yearsExperience": 3,
        },
        "conversation_history": [
            {"role": "assistant", "content": "Let's look at Day 1: VS Code & Python Environment Setup. Can you explain how you use Python and VS Code in your workflow?"}
        ],
        "completed_curriculum_days": [1, 2, 3, 4, 5, 6],
        "questions_asked": [
            "Let's look at Day 1: VS Code & Python Environment Setup. Can you explain how you use Python and VS Code in your workflow?"
        ],
        "curriculum_days_covered": [1],
        "number_of_questions_asked": 1,
        "current_question": "Let's look at Day 1: VS Code & Python Environment Setup. Can you explain how you use Python and VS Code in your workflow?",
        "current_topic": "Day 1: VS Code & Python Environment Setup",
        "is_completed": False,
        "collected_information": {},
        "feedback": None,
        "last_message": "I use Python for scripting and VS Code for debugging.",
    }

    first_result = generate_question(state)
    second_result = generate_question({**state, "questions_asked": first_result["questions_asked"], "conversation_history": first_result["conversation_history"], "curriculum_days_covered": first_result["curriculum_days_covered"], "number_of_questions_asked": first_result["number_of_questions_asked"]})

    assert first_result["current_question"] != second_result["current_question"]
    assert second_result["current_question"] not in state["questions_asked"]
