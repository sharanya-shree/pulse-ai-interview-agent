import json
import re
from typing import TypedDict, List, Dict, Any, Optional

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import settings
from app.services.curriculum import CurriculumService


# ============================================================
# LANGGRAPH STATE
# ============================================================

class AgentState(TypedDict):
    session_id: str
    candidate_data: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    completed_curriculum_days: List[int]
    questions_asked: List[str]
    curriculum_days_covered: List[int]
    number_of_questions_asked: int
    current_question: str
    current_topic: str
    is_completed: bool
    collected_information: Dict[str, Any]
    feedback: Optional[Dict[str, Any]]
    last_message: Optional[str]


# ============================================================
# CURRICULUM SERVICE
# ============================================================

curriculum_service = CurriculumService()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _normalize_text(value: Optional[str]) -> str:
    """
    Convert None to an empty string and remove unnecessary
    whitespace.
    """
    return (value or "").strip()


def _normalize_candidate_data(
    candidate_data: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Normalize candidate information so the rest of the workflow
    can safely use consistent field names and default values.
    """

    if not isinstance(candidate_data, dict):
        return {}

    normalized = dict(candidate_data)

    # Candidate name
    normalized["name"] = (
        _normalize_text(candidate_data.get("name"))
        or "Candidate"
    )

    # Job role
    normalized["jobRole"] = (
        _normalize_text(
            candidate_data.get("jobRole")
            or candidate_data.get("job_role")
        )
        or "Software Engineer"
    )

    # Experience level
    normalized["experienceLevel"] = (
        _normalize_text(
            candidate_data.get("experienceLevel")
            or candidate_data.get("experience_level")
        )
        or "Intermediate"
    )

    # Years of experience
    years_exp = candidate_data.get(
        "yearsExperience",
        candidate_data.get("years_experience", 3),
    )

    try:
        normalized["yearsExperience"] = int(years_exp)
    except (TypeError, ValueError):
        normalized["yearsExperience"] = 3

    # Completed curriculum days
    completed_days = candidate_data.get(
        "completedDays",
        candidate_data.get("completed_days", []),
    )

    if isinstance(completed_days, list):
        normalized["completedDays"] = [
            int(day)
            for day in completed_days
            if str(day).strip().isdigit()
        ]
    else:
        normalized["completedDays"] = []

    return normalized


def _clean_question(question: str) -> str:
    """
    Clean Gemini's response so that only the interview question
    is displayed.
    """

    cleaned = _normalize_text(question)

    # Remove markdown formatting
    cleaned = re.sub(r"^\s*#+\s*", "", cleaned)
    cleaned = re.sub(r"^\s*[-*]\s*", "", cleaned)

    # Remove common prefixes
    prefixes = [
        "Question:",
        "Interview Question:",
        "Technical Question:",
        "Here is the question:",
        "Here’s the question:",
    ]

    for prefix in prefixes:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()

    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned


def _ensure_unique_question(
    question: str,
    existing_questions: List[str],
) -> str:
    """
    Make sure the generated question does not exactly duplicate
    an earlier question.
    """

    cleaned = _clean_question(question)

    if not cleaned:
        return (
            "Can you explain how you would apply this concept "
            "in a real-world technical project?"
        )

    seen = {
        re.sub(
            r"\s+",
            " ",
            _normalize_text(existing),
        ).lower()
        for existing in existing_questions or []
        if _normalize_text(existing)
    }

    if cleaned.lower() not in seen:
        return cleaned

    return (
        f"{cleaned} "
        "Can you also describe a practical implementation example?"
    )


def _format_tools(tools: List[str]) -> str:
    """
    Format a list of tools naturally for an LLM prompt.
    """

    if not tools:
        return "the relevant technologies"

    if len(tools) == 1:
        return tools[0]

    if len(tools) == 2:
        return f"{tools[0]} and {tools[1]}"

    return ", ".join(tools[:-1]) + f", and {tools[-1]}"


def _build_question_text(
    is_followup: bool,
    next_day: int,
    day_title: str,
    day_tools: List[str],
    day_objectives: List[str],
    last_message: Optional[str],
    candidate_name: str,
    job_role: str,
    experience_level: str,
    years_exp: int,
) -> str:
    """
    Safe fallback question generator.

    This is only used when Gemini cannot generate a question.
    """

    tools = day_tools[:2] if day_tools else [
        "the relevant technologies"
    ]

    tools_text = _format_tools(tools)

    objective = (
        day_objectives[0]
        if day_objectives
        else "the core concepts of this topic"
    )

    objective = objective.strip()

    # Remove instructional prefixes from curriculum objectives
    prefixes_to_remove = [
        "understand how ",
        "understand ",
        "learn how ",
        "learn ",
        "explain how ",
        "explain ",
        "know how ",
        "know ",
    ]

    clean_objective = objective

    for prefix in prefixes_to_remove:
        if clean_objective.lower().startswith(prefix):
            clean_objective = clean_objective[len(prefix):]
            break

    if is_followup:
        answer = _normalize_text(last_message)

        if answer:
            answer = answer[:160]

            return (
                f"You mentioned that {answer}. "
                f"What would you change or improve in that approach "
                f"when working with {tools_text}?"
            )

        return (
            f"How would you validate your approach to "
            f"{clean_objective.lower()} using {tools_text}?"
        )

    return (
        f"As a {experience_level} {job_role} with "
        f"{years_exp} years of experience, how would you approach "
        f"{clean_objective.lower()} using {tools_text} "
        f"in a real-world project?"
    )


def _create_gemini() -> ChatGoogleGenerativeAI:
    """
    Create the Gemini model using the API key and model configured
    in app.core.config.
    """

    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7,
    )


# ============================================================
# EVALUATE CANDIDATE ANSWER
# ============================================================

def evaluate_answer(state: AgentState) -> Dict[str, Any]:
    """
    Evaluate the candidate's latest answer using Gemini.
    """

    last_msg = state.get("last_message")
    current_q = state.get("current_question")
    current_t = state.get("current_topic")
    history = state.get("conversation_history") or []

    # No answer means the interview is just starting.
    if not _normalize_text(last_msg):
        return {
            "conversation_history": history
        }

    # Copy conversation history
    new_history = list(history)

    # Store candidate answer
    new_history.append(
        {
            "role": "user",
            "content": _normalize_text(last_msg),
        }
    )

    collected_info = dict(
        state.get("collected_information") or {}
    )

    # --------------------------------------------------------
    # Gemini evaluation
    # --------------------------------------------------------

    if settings.GOOGLE_API_KEY:

        try:
            llm = _create_gemini()

            prompt = (
                "You are evaluating a candidate in a technical "
                "interview.\n\n"

                f"Interview Topic: {current_t}\n"
                f"Interview Question: {current_q}\n\n"

                f"Candidate Answer:\n{last_msg}\n\n"

                "Evaluate the answer based on technical correctness, "
                "clarity, depth, and practical understanding.\n\n"

                "Give a concise evaluation in 2-4 sentences.\n"
                "Mention what the candidate did well and identify "
                "any important technical gap or misconception.\n"

                "Do not give a numerical score.\n"
                "Do not address the candidate directly.\n"
            )

            response = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "You are a precise and fair technical "
                            "interviewer. Evaluate answers objectively."
                        )
                    ),
                    HumanMessage(content=prompt),
                ]
            )

            assessment = _normalize_text(
                str(response.content)
            )

        except Exception as e:
            assessment = (
                "Gemini evaluation was temporarily unavailable. "
                "The candidate's answer was recorded successfully."
            )

    else:
        assessment = (
            "LLM evaluation is unavailable because the Gemini "
            "API key is not configured. The answer was recorded."
        )

    # Store evaluation
    collected_info[current_t or "General"] = {
        "question": current_q,
        "answer": last_msg,
        "assessment": assessment,
    }

    return {
        "conversation_history": new_history,
        "collected_information": collected_info,
    }


# ============================================================
# GENERATE NEXT INTERVIEW QUESTION
# ============================================================

def generate_question(state: AgentState) -> Dict[str, Any]:
    """
    Select the next curriculum day and generate an intelligent
    interview question using Gemini.
    """

    candidate = _normalize_candidate_data(
        state.get("candidate_data") or {}
    )

    history = state.get("conversation_history") or []

    questions_asked = list(
        state.get("questions_asked") or []
    )

    days_covered = list(
        state.get("curriculum_days_covered") or []
    )

    # --------------------------------------------------------
    # Candidate information
    # --------------------------------------------------------

    name = candidate.get("name") or "Candidate"

    job_role = (
        candidate.get("jobRole")
        or "Software Engineer"
    )

    experience_level = (
        candidate.get("experienceLevel")
        or "Intermediate"
    )

    years_exp = (
        candidate.get("yearsExperience")
        or 3
    )

    # --------------------------------------------------------
    # Determine curriculum days
    # --------------------------------------------------------

    completed_days = list(
        state.get("completed_curriculum_days") or []
    )

    target_days = list(completed_days)

    # Make sure we have at least 6 curriculum days
    if len(target_days) < 6:

        all_days = [
            d["day"]
            for d in curriculum_service.data.get(
                "days",
                [],
            )
        ]

        for day_number in all_days:

            if day_number not in target_days:
                target_days.append(day_number)

            if len(target_days) >= 6:
                break

    # --------------------------------------------------------
    # Determine current day
    # --------------------------------------------------------

    current_day = None

    current_topic = state.get("current_topic")

    if current_topic and current_topic.startswith("Day "):

        try:
            current_day = int(
                current_topic.split(" ")[1].rstrip(":")
            )

        except (ValueError, IndexError):
            current_day = None

    # --------------------------------------------------------
    # Decide follow-up vs new topic
    # --------------------------------------------------------

    ask_followup = False

    if current_day is not None:

        last_msg = _normalize_text(
            state.get("last_message")
        )

        day_count = days_covered.count(current_day)

        if day_count == 1 and last_msg:

            unique_days_so_far = len(
                set(days_covered)
            )

            remaining_questions = (
                10 - len(questions_asked)
            )

            unique_days_needed = (
                6 - unique_days_so_far
            )

            if remaining_questions > unique_days_needed:
                ask_followup = True

    # --------------------------------------------------------
    # Select next day
    # --------------------------------------------------------

    if ask_followup and current_day is not None:

        next_day = current_day
        is_followup = True

    else:

        next_day = None

        # Prefer a curriculum day that has not been covered
        for day_number in target_days:

            if day_number not in days_covered:
                next_day = day_number
                break

        # If all days are covered, choose the least-used day
        if next_day is None:

            day_counts = {
                day_number: days_covered.count(day_number)
                for day_number in target_days
            }

            if day_counts:
                next_day = min(
                    day_counts,
                    key=day_counts.get,
                )
            else:
                next_day = 1

        is_followup = False

    # --------------------------------------------------------
    # Get curriculum information
    # --------------------------------------------------------

    day_info = (
        curriculum_service.get_day(next_day)
        or {}
    )

    day_title = day_info.get(
        "title",
        "Software Engineering Concepts",
    )

    day_tools = day_info.get(
        "tools",
        [],
    )

    day_objectives = day_info.get(
        "objectives",
        [],
    )

    topic_label = (
        f"Day {next_day}: {day_title}"
    )

    last_message = state.get("last_message")

    # --------------------------------------------------------
    # Gemini question generation
    # --------------------------------------------------------

    if settings.GOOGLE_API_KEY:

        try:

            llm = _create_gemini()

            # Keep only recent conversation to avoid huge prompts
            recent_history = history[-8:]

            history_text = "\n".join(
                [
                    f"{message.get('role', 'unknown').capitalize()}: "
                    f"{message.get('content', '')}"
                    for message in recent_history
                ]
            )

            tools_text = _format_tools(day_tools)

            objectives_text = (
                "; ".join(day_objectives)
                if day_objectives
                else "the core concepts of the topic"
            )

            previous_questions = "\n".join(
                [
                    f"- {question}"
                    for question in questions_asked[-8:]
                ]
            )

            # ------------------------------------------------
            # Strong Gemini instruction
            # ------------------------------------------------

            prompt = (
                "You are an expert technical interviewer "
                "conducting a realistic software engineering "
                "interview.\n\n"

                f"Candidate name: {name}\n"
                f"Job role: {job_role}\n"
                f"Experience level: {experience_level}\n"
                f"Years of experience: {years_exp}\n\n"

                f"Current curriculum topic: {day_title}\n"
                f"Relevant technologies/tools: {tools_text}\n"
                f"Learning objectives: {objectives_text}\n\n"

                f"Recent conversation:\n"
                f"{history_text or 'No previous conversation.'}\n\n"

                f"Previously asked questions:\n"
                f"{previous_questions or 'No previous questions.'}\n\n"
            )

            if is_followup:

                prompt += (
                    "This is a FOLLOW-UP question.\n\n"

                    f"The candidate's previous answer was:\n"
                    f"{last_message}\n\n"

                    "Analyze the candidate's previous answer and "
                    "ask ONE meaningful follow-up question.\n"

                    "The follow-up should test deeper understanding, "
                    "reasoning, trade-offs, debugging, design choices, "
                    "or practical implementation.\n"

                    "Do not simply ask the candidate to repeat or "
                    "rephrase their previous answer.\n"

                    "Do not mention that this is a follow-up."
                )

            else:

                prompt += (
                    "This is a NEW topic.\n\n"

                    "Ask ONE technical interview question that "
                    "directly tests one of the listed learning "
                    "objectives.\n"

                    "The question should be appropriate for the "
                    "candidate's experience level.\n"

                    "Prefer practical and scenario-based questions "
                    "over simple definitions.\n"

                    "The question should sound like something a "
                    "real technical interviewer would ask."
                )

            prompt += (
                "\n\nIMPORTANT OUTPUT RULES:\n"
                "1. Output exactly ONE interview question.\n"
                "2. Output only the question.\n"
                "3. Do not include 'Question:' or any heading.\n"
                "4. Do not provide the answer.\n"
                "5. Do not explain your reasoning.\n"
                "6. Do not repeat an earlier question.\n"
                "7. Keep the question clear and conversational.\n"
                "8. Avoid awkward phrases such as 'explain how X "
                "can be used to how Y'.\n"
            )

            response = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "You are a professional AI technical "
                            "interviewer. Your questions must be "
                            "natural, technically meaningful, and "
                            "grammatically correct."
                        )
                    ),
                    HumanMessage(content=prompt),
                ]
            )

            question = _clean_question(
                str(response.content)
            )

        except Exception:

            # Safe fallback if Gemini fails
            question = _build_question_text(
                is_followup=is_followup,
                next_day=next_day,
                day_title=day_title,
                day_tools=day_tools,
                day_objectives=day_objectives,
                last_message=last_message,
                candidate_name=name,
                job_role=job_role,
                experience_level=experience_level,
                years_exp=years_exp,
            )

    else:

        # Gemini API key not configured
        question = _build_question_text(
            is_followup=is_followup,
            next_day=next_day,
            day_title=day_title,
            day_tools=day_tools,
            day_objectives=day_objectives,
            last_message=last_message,
            candidate_name=name,
            job_role=job_role,
            experience_level=experience_level,
            years_exp=years_exp,
        )

    # --------------------------------------------------------
    # Prevent duplicate questions
    # --------------------------------------------------------

    question = _ensure_unique_question(
        question,
        questions_asked,
    )

    # --------------------------------------------------------
    # Update conversation history
    # --------------------------------------------------------

    new_history = list(history)

    new_history.append(
        {
            "role": "assistant",
            "content": question,
        }
    )

    # --------------------------------------------------------
    # Update question tracking
    # --------------------------------------------------------

    new_questions = list(questions_asked)

    new_questions.append(question)

    new_days_covered = list(days_covered)

    new_days_covered.append(next_day)

    # --------------------------------------------------------
    # Return updated state
    # --------------------------------------------------------

    return {
        "conversation_history": new_history,
        "questions_asked": new_questions,
        "curriculum_days_covered": new_days_covered,
        "number_of_questions_asked": len(
            new_questions
        ),
        "current_question": question,
        "current_topic": topic_label,
        "last_message": None,
    }


# ============================================================
# GENERATE FINAL FEEDBACK
# ============================================================

def generate_feedback(
    state: AgentState,
) -> Dict[str, Any]:
    """
    Generate final structured interview feedback using Gemini.
    """

    candidate = (
        state.get("candidate_data")
        or {}
    )

    history = (
        state.get("conversation_history")
        or []
    )

    collected_info = (
        state.get("collected_information")
        or {}
    )

    name = candidate.get(
        "name",
        "Candidate",
    )

    job_role = (
        candidate.get("jobRole")
        or candidate.get("job_role")
        or "Software Engineer"
    )

    # --------------------------------------------------------
    # Gemini final evaluation
    # --------------------------------------------------------

    if settings.GOOGLE_API_KEY:

        try:

            llm = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.2,
            )

            evals = []

            for topic, details in collected_info.items():

                evals.append(
                    (
                        f"Topic: {topic}\n"
                        f"Question: {details.get('question')}\n"
                        f"Answer: {details.get('answer')}\n"
                        f"Assessment: "
                        f"{details.get('assessment')}\n"
                    )
                )

            evals_summary = "\n".join(evals)

            prompt = (
                "You are a senior technical interviewer "
                "writing the final evaluation of a candidate.\n\n"

                f"Candidate: {name}\n"
                f"Role: {job_role}\n\n"

                "Interview evaluations:\n"
                f"{evals_summary}\n\n"

                "Based ONLY on the interview evidence above, "
                "generate a structured evaluation.\n\n"

                "Return ONLY valid JSON using exactly this structure:\n"

                "{\n"
                '  "summary": "Overall assessment",\n'
                '  "strengths": ['
                '"Strength 1", "Strength 2"'
                '],\n'
                '  "gaps": ['
                '"Gap 1", "Gap 2"'
                '],\n'
                '  "next": ['
                '"Recommendation 1", "Recommendation 2"'
                "]\n"
                "}\n\n"

                "Rules:\n"
                "- Do not use markdown.\n"
                "- Do not include a preamble.\n"
                "- Do not invent technologies that were not discussed.\n"
                "- Keep the feedback specific to the candidate's answers."
            )

            response = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "You are a precise technical evaluator "
                            "who outputs strictly valid JSON."
                        )
                    ),
                    HumanMessage(content=prompt),
                ]
            )

            json_text = _normalize_text(
                str(response.content)
            )

            # Remove markdown code fences if Gemini adds them
            if json_text.startswith("```"):

                lines = json_text.splitlines()

                if len(lines) >= 3:
                    json_text = "\n".join(
                        lines[1:-1]
                    ).strip()

            feedback_data = json.loads(
                json_text
            )

        except Exception:

            feedback_data = {
                "summary": (
                    "The technical interview was completed "
                    "successfully. The candidate demonstrated "
                    "knowledge across the evaluated curriculum areas."
                ),
                "strengths": [
                    "Demonstrated understanding of the "
                    "interviewed technical concepts.",
                    "Provided structured responses "
                    "during the interview."
                ],
                "gaps": [
                    "Some technical areas could be explored "
                    "in greater depth."
                ],
                "next": [
                    "Practice deeper system design and "
                    "real-world implementation scenarios."
                ],
            }

    else:

        feedback_data = {
            "summary": (
                f"Technical interview completed for "
                f"{name} ({job_role})."
            ),
            "strengths": [
                "Demonstrated familiarity with the "
                "interviewed technical topics.",
                "Provided responses throughout the interview."
            ],
            "gaps": [
                "Some technical concepts could be "
                "explored in greater depth."
            ],
            "next": [
                "Practice real-world implementation "
                "and troubleshooting scenarios."
            ],
        }

    # --------------------------------------------------------
    # Final assistant message
    # --------------------------------------------------------

    reply = (
        "Thank you for completing your interview. "
        "Your structured feedback and evaluation have "
        "been compiled successfully."
    )

    new_history = list(history)

    new_history.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    return {
        "conversation_history": new_history,
        "is_completed": True,
        "feedback": feedback_data,
    }


# ============================================================
# DECIDE NEXT STEP
# ============================================================

def decide_next_step(
    state: AgentState,
) -> str:
    """
    Decide whether to generate another question or finish
    the interview.
    """

    questions_count = len(
        state.get("questions_asked") or []
    )

    days_covered = set(
        state.get("curriculum_days_covered")
        or []
    )

    if state.get("is_completed"):
        return "generate_feedback"

    # Interview requirements:
    # At least 10 questions
    # At least 6 unique curriculum days

    if (
        questions_count >= 10
        and len(days_covered) >= 6
    ):
        return "generate_feedback"

    return "generate_question"


# ============================================================
# BUILD LANGGRAPH WORKFLOW
# ============================================================

workflow = StateGraph(AgentState)


# ------------------------------------------------------------
# Add nodes
# ------------------------------------------------------------

workflow.add_node(
    "evaluate_answer",
    evaluate_answer,
)

workflow.add_node(
    "generate_question",
    generate_question,
)

workflow.add_node(
    "generate_feedback",
    generate_feedback,
)


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

workflow.set_entry_point(
    "evaluate_answer"
)


# ------------------------------------------------------------
# Conditional routing
# ------------------------------------------------------------

workflow.add_conditional_edges(
    "evaluate_answer",
    decide_next_step,
    {
        "generate_question": "generate_question",
        "generate_feedback": "generate_feedback",
    },
)


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------

workflow.add_edge(
    "generate_question",
    END,
)

workflow.add_edge(
    "generate_feedback",
    END,
)


# ------------------------------------------------------------
# Compile graph
# ------------------------------------------------------------

compiled_graph = workflow.compile()