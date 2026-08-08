import json
import re
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.core.config import settings
from app.services.curriculum import CurriculumService

# Define LangGraph AgentState
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

# Initialize CurriculumService helper
curriculum_service = CurriculumService()


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()


def _normalize_candidate_data(candidate_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(candidate_data, dict):
        return {}

    normalized = dict(candidate_data)
    normalized["name"] = _normalize_text(candidate_data.get("name")) or "Candidate"
    normalized["jobRole"] = _normalize_text(
        candidate_data.get("jobRole") or candidate_data.get("job_role")
    ) or "Software Engineer"
    normalized["experienceLevel"] = _normalize_text(
        candidate_data.get("experienceLevel") or candidate_data.get("experience_level")
    ) or "Intermediate"

    years_exp = candidate_data.get("yearsExperience", candidate_data.get("years_experience", 3))
    try:
        normalized["yearsExperience"] = int(years_exp)
    except (TypeError, ValueError):
        normalized["yearsExperience"] = 3

    completed_days = candidate_data.get("completedDays", candidate_data.get("completed_days", []))
    if isinstance(completed_days, list):
        normalized["completedDays"] = [
            int(day) for day in completed_days if str(day).strip().isdigit()
        ]
    else:
        normalized["completedDays"] = []

    return normalized


def _ensure_unique_question(question: str, existing_questions: List[str]) -> str:
    cleaned = re.sub(r"\s+", " ", _normalize_text(question))
    if not cleaned:
        return "Could you walk me through a concrete implementation example for this topic?"

    seen = {
        re.sub(r"\s+", " ", _normalize_text(existing))
        for existing in existing_questions or []
        if _normalize_text(existing)
    }
    if cleaned not in seen:
        return cleaned

    return f"{cleaned} Please share a concrete implementation example."


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
    tools = day_tools[:2] if day_tools else ["these tools"]
    objectives = day_objectives[0] if day_objectives else "the module objective"

    if is_followup:
        answer_excerpt = _normalize_text(last_message)
        if answer_excerpt:
            answer_excerpt = answer_excerpt[:120]
            return (
                f"Building on your note about {answer_excerpt}, how would you validate or improve that approach "
                f"for {day_title} using {', '.join(tools)}?"
            )
        return (
            f"Regarding {day_title}, how would you validate or improve your approach using {', '.join(tools)}?"
        )

    return (
        f"{candidate_name}, as a {experience_level.lower()} {job_role.lower()}, how would you apply "
        f"{', '.join(tools)} to address {objectives} for {day_title}?"
    )


def evaluate_answer(state: AgentState) -> Dict[str, Any]:
    """Node: Evaluates the candidate's last answer and updates collected_information."""
    last_msg = state.get("last_message")
    current_q = state.get("current_question")
    current_t = state.get("current_topic")
    history = state.get("conversation_history") or []
    
    # If starting session (no answer yet), do nothing
    if not _normalize_text(last_msg):
        return {"conversation_history": history}

    # Append candidate's response to history
    new_history = list(history)
    new_history.append({"role": "user", "content": _normalize_text(last_msg)})

    collected_info = dict(state.get("collected_information") or {})

    # Evaluate the answer (Dual mode: Real LLM or Mock fallback)
    if settings.OPENAI_API_KEY:
        try:
            llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.2)
            prompt = (
                f"You are a technical interviewer. Evaluate the candidate's answer for the following topic/question.\n\n"
                f"Topic: {current_t}\n"
                f"Question: {current_q}\n"
                f"Candidate Answer: {last_msg}\n\n"
                f"Provide a concise summary assessing the candidate's understanding (1-2 sentences). Mention any strengths or clear gaps."
            )
            response = llm.invoke([SystemMessage(content="You are a precise technical evaluator."), HumanMessage(content=prompt)])
            assessment = response.content.strip()
        except Exception as e:
            assessment = f"Evaluation (API fallback): Candidate responded on {current_t}. Answer was logged successfully."
    else:
        assessment = f"Mock evaluation for '{current_t}': Answer '{last_msg}' shows satisfactory understanding of target tools."

    # Store evaluation under current topic
    collected_info[current_t or "General"] = {
        "question": current_q,
        "answer": last_msg,
        "assessment": assessment
    }

    return {
        "conversation_history": new_history,
        "collected_information": collected_info
    }

def generate_question(state: AgentState) -> Dict[str, Any]:
    """Node: Selects the next curriculum day and generates a personalized question."""
    candidate = _normalize_candidate_data(state.get("candidate_data") or {})
    history = state.get("conversation_history") or []
    questions_asked = list(state.get("questions_asked") or [])
    days_covered = list(state.get("curriculum_days_covered") or [])
    
    # Extract candidate metadata
    name = candidate.get("name") or "Candidate"
    job_role = candidate.get("jobRole") or "Software Engineer"
    experience_level = candidate.get("experienceLevel") or "Intermediate"
    years_exp = candidate.get("yearsExperience") or 3
    
    # Establish target curriculum days to cover
    completed_days = list(state.get("completed_curriculum_days") or [])
    target_days = list(completed_days)
    
    # If candidate completed less than 6 days, pad list with default curriculum days
    if len(target_days) < 6:
        all_days = [d["day"] for d in curriculum_service.data.get("days", [])]
        for d in all_days:
            if d not in target_days:
                target_days.append(d)
            if len(target_days) >= 6:
                break

    # Determine whether we ask a follow-up on the current day or switch to a new day
    current_day = None
    current_topic = state.get("current_topic")
    if current_topic and current_topic.startswith("Day "):
        try:
            current_day = int(current_topic.split(" ")[1].rstrip(":"))
        except ValueError:
            pass

    ask_followup = False
    if current_day is not None:
        # Follow-up questions should only be used when the prior answer exists and there is still room to cover more unique days.
        last_msg = _normalize_text(state.get("last_message"))
        day_count = days_covered.count(current_day)
        if day_count == 1 and last_msg:
            unique_days_so_far = len(set(days_covered))
            remaining_questions = 10 - len(questions_asked)
            unique_days_needed = 6 - unique_days_so_far
            if remaining_questions > unique_days_needed:
                ask_followup = True

    if ask_followup and current_day is not None:
        next_day = current_day
        is_followup = True
    else:
        # Switch to a day that hasn't been covered yet
        next_day = None
        for day_num in target_days:
            if day_num not in days_covered:
                next_day = day_num
                break
        
        # If all target days are covered, pick the one with fewest questions asked
        if next_day is None:
            day_counts = {d: days_covered.count(d) for d in target_days}
            next_day = min(day_counts, key=day_counts.get)
            
        is_followup = False

    # Get details of target day
    day_info = curriculum_service.get_day(next_day) or {}
    day_title = day_info.get("title", "Software Engineering Concepts")
    day_tools = day_info.get("tools", [])
    day_objectives = day_info.get("objectives", [])

    topic_label = f"Day {next_day}: {day_title}"

    # Generate question text (Dual mode: Real LLM or Mock fallback)
    last_message = state.get("last_message")
    if settings.OPENAI_API_KEY:
        try:
            llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.7)
            
            # Format history
            hist_str = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history[-6:]])
            
            prompt = (
                f"You are conducting a personalized, conversational technical interview for a {job_role} role.\n"
                f"Candidate Name: {name}\n"
                f"Experience Level: {experience_level} ({years_exp} years experience)\n"
                f"Topic: Day {next_day} - {day_title}\n"
                f"Tools involved: {', '.join(day_tools)}\n"
                f"Objectives: {'; '.join(day_objectives)}\n\n"
                f"Recent Conversation History:\n{hist_str}\n\n"
            )
            if is_followup:
                prompt += (
                    "This is a follow-up question. Use the candidate's last answer as context and ask an intelligent, "
                    f"personalized follow-up based on their response: {last_message}."
                )
            else:
                prompt += (
                    "This is a new topic. Introduce the topic with a natural transition, and ask a personalized "
                    "technical question targeting one of the day's objectives."
                )
            prompt += "\n\nAsk the question directly. Do not include any meta-text, headers, or prefix. Avoid repeating the exact same question as earlier turns."
            
            response = llm.invoke([SystemMessage(content="You are a friendly, professional AI technical interviewer."), HumanMessage(content=prompt)])
            question = response.content.strip()
        except Exception:
            # Safe fallback if API call fails
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
        # Mock question output
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

    question = _ensure_unique_question(question, questions_asked)

    # Append to history & tracking
    new_history = list(history)
    new_history.append({"role": "assistant", "content": question})
    new_questions = list(questions_asked)
    new_questions.append(question)
    new_days_covered = list(days_covered)
    new_days_covered.append(next_day)

    return {
        "conversation_history": new_history,
        "questions_asked": new_questions,
        "curriculum_days_covered": new_days_covered,
        "number_of_questions_asked": len(new_questions),
        "current_question": question,
        "current_topic": topic_label,
        "last_message": None  # Reset for next turn
    }

def generate_feedback(state: AgentState) -> Dict[str, Any]:
    """Node: Generates the final structured feedback report when the interview ends."""
    candidate = state.get("candidate_data") or {}
    history = state.get("conversation_history") or []
    collected_info = state.get("collected_information") or {}
    
    name = candidate.get("name") or "Candidate"
    job_role = candidate.get("jobRole") or candidate.get("job_role") or "Software Engineer"
    
    # Generate structured feedback (Dual mode: Real LLM or Mock fallback)
    if settings.OPENAI_API_KEY:
        try:
            llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.2)
            
            # Format collected evaluations
            evals_summary = ""
            for topic, details in collected_info.items():
                evals_summary += f"- Topic: {topic}\n  Q: {details.get('question')}\n  A: {details.get('answer')}\n  Assessment: {details.get('assessment')}\n\n"
                
            prompt = (
                f"You are a principal technical evaluator writing a final interview report for candidate {name} (applying for {job_role}).\n\n"
                f"Review the evaluations collected during the interview:\n{evals_summary}\n\n"
                f"Generate structured feedback. You MUST output a valid JSON object matching the schema below. Do not output markdown, preambles, or postambles. Only output raw JSON:\n"
                f"{{\n"
                f"  \"summary\": \"Overall summary of the candidate's performance.\",\n"
                f"  \"strengths\": [\"Strength 1\", \"Strength 2\"],\n"
                f"  \"gaps\": [\"Gap 1\", \"Gap 2\"],\n"
                f"  \"next\": [\"Recommendation 1\", \"Recommendation 2\"]\n"
                f"}}"
            )
            
            response = llm.invoke([
                SystemMessage(content="You are a precise technical evaluator that outputs strictly valid JSON."),
                HumanMessage(content=prompt)
            ])
            
            # Parse JSON response
            json_text = response.content.strip()
            # Handle markdown code blocks if the LLM outputted them despite instructions
            if json_text.startswith("```"):
                lines = json_text.splitlines()
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    json_text = "\n".join(lines[1:-1])
                    
            feedback_data = json.loads(json_text)
        except Exception as e:
            # Fallback mock feedback if parsing or API fails
            feedback_data = {
                "summary": f"Technical evaluation completed. The candidate showed solid familiarity with their completed curriculum topics.",
                "strengths": ["Demonstrated knowledge of their listed daily syllabus modules.", "Conversational and structured answers."],
                "gaps": ["Some specific tooling configuration details were omitted during conversation."],
                "next": ["Review objectives and practice deployment configurations."]
            }
    else:
        # Mock feedback
        feedback_data = {
            "summary": f"Technical interview completed for {name} ({job_role}). Demonstrated comprehension across {len(collected_info)} covered syllabus areas.",
            "strengths": [
                "Good familiarity with setup and development requirements.",
                "Provided coherent code explanations during dialogue turns."
            ],
            "gaps": [
                "Could expand more on debugging multi-agent coordination states.",
                "Deep dive into Docker network configs is recommended."
            ],
            "next": [
                "Proceed to advanced deployment modules (Kubernetes/Docker).",
                "Practice implementing mock LangGraph graphs and checkpoints."
            ]
        }

    # Add final wrap-up reply text
    reply = "Thank you for completing your interview. Your structured feedback and evaluation have been compiled successfully."
    
    new_history = list(history)
    new_history.append({"role": "assistant", "content": reply})

    return {
        "conversation_history": new_history,
        "is_completed": True,
        "feedback": feedback_data
    }

def decide_next_step(state: AgentState) -> str:
    """Conditional Edge router: Determines if the interview has reached termination requirements."""
    questions_count = len(state.get("questions_asked") or [])
    days_covered = set(state.get("curriculum_days_covered") or [])
    
    if state.get("is_completed"):
        return "generate_feedback"

    # Requirement: Target at least 10 questions AND cover at least 6 unique days
    if questions_count >= 10 and len(days_covered) >= 6:
        return "generate_feedback"
    return "generate_question"

# Construct and compile LangGraph StateGraph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("evaluate_answer", evaluate_answer)
workflow.add_node("generate_question", generate_question)
workflow.add_node("generate_feedback", generate_feedback)

# Define entry point
workflow.set_entry_point("evaluate_answer")

# Add conditional routing
workflow.add_conditional_edges(
    "evaluate_answer",
    decide_next_step,
    {
        "generate_question": "generate_question",
        "generate_feedback": "generate_feedback"
    }
)

# Connect execution endpoints
workflow.add_edge("generate_question", END)
workflow.add_edge("generate_feedback", END)

# Compile
compiled_graph = workflow.compile()
