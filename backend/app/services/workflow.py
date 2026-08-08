import json
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

def evaluate_answer(state: AgentState) -> Dict[str, Any]:
    """Node: Evaluates the candidate's last answer and updates collected_information."""
    last_msg = state.get("last_message")
    current_q = state.get("current_question")
    current_t = state.get("current_topic")
    history = state.get("conversation_history") or []
    
    # If starting session (no answer yet), do nothing
    if not last_msg:
        return {"conversation_history": history}

    # Append candidate's response to history
    new_history = list(history)
    new_history.append({"role": "user", "content": last_msg})

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
    candidate = state.get("candidate_data") or {}
    history = state.get("conversation_history") or []
    questions_asked = list(state.get("questions_asked") or [])
    days_covered = list(state.get("curriculum_days_covered") or [])
    
    # Extract candidate metadata
    name = candidate.get("name") or "Candidate"
    job_role = candidate.get("jobRole") or candidate.get("job_role") or "Software Engineer"
    experience_level = candidate.get("experienceLevel") or candidate.get("experience_level") or "Intermediate"
    years_exp = candidate.get("yearsExperience") or candidate.get("years_experience") or 3
    
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
        # How many times have we asked about this day?
        day_count = days_covered.count(current_day)
        if day_count == 1:
            # Check if switching is mandatory to cover 6 unique days
            unique_days_so_far = len(set(days_covered))
            remaining_questions = 10 - len(questions_asked)
            unique_days_needed = 6 - unique_days_so_far
            if remaining_questions > unique_days_needed:
                # Room for a follow-up question
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
                    "This is a follow-up question. Based on the candidate's last answer, ask an intelligent, "
                    "personalized follow-up to dive deeper into the topic, or clarify a gap."
                )
            else:
                prompt += (
                    "This is a new topic. Introduce the topic with a natural transition, and ask a personalized "
                    "technical question targeting one of the day's objectives."
                )
            prompt += "\n\nAsk the question directly. Do not include any meta-text, headers, or prefix."
            
            response = llm.invoke([SystemMessage(content="You are a friendly, professional AI technical interviewer."), HumanMessage(content=prompt)])
            question = response.content.strip()
        except Exception as e:
            # Safe fallback if API call fails
            if is_followup:
                question = f"That's interesting. Regarding the tools in Day {next_day} ({day_title}), how would you handle scaling or error recovery for that setup?"
            else:
                question = f"Let's move on to Day {next_day}: {day_title}. Could you explain your experience using {day_tools[0] if day_tools else 'these tools'} and how you implemented their core objectives?"
    else:
        # Mock question output
        if is_followup:
            question = f"Follow-up on Day {next_day} ({day_title}): How do you handle failure modes or ensure scalability using {', '.join(day_tools[:2])}?"
        else:
            question = f"Let's look at Day {next_day}: {day_title}. Can you explain how you would apply {', '.join(day_tools[:2])} to fulfill the objectives of this module?"

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
