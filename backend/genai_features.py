"""
Additional GenAI-powered features for Jetski SmartHire, built on top of
the same Gemini model used for screening.
"""
import google.generativeai as genai


def generate_cover_letter(resume_text: str, job_description: str, tone: str = "professional") -> str:
    prompt = f"""Using the resume and job description below, write a tailored cover letter.

Tone: {tone}

RESUME:
{resume_text[:8000]}

JOB DESCRIPTION:
{job_description[:4000]}

Write a concise, 3-4 paragraph cover letter. Address it generically ("Dear Hiring Manager")
since no company contact name was given. Return plain text only, no markdown headers."""

    model = genai.GenerativeModel(genai_model_name())
    response = model.generate_content(prompt)
    return response.text.strip()


def suggest_resume_improvements(resume_text: str, job_description: str = "") -> str:
    context = f"\n\nTarget job description:\n{job_description[:3000]}" if job_description else ""
    prompt = f"""Review this resume and suggest concrete improvements: wording, structure,
missing sections, quantifying achievements, and (if a job description is given) better
alignment with that role.

RESUME:
{resume_text[:8000]}{context}

Return a short bullet list of specific, actionable suggestions."""

    model = genai.GenerativeModel(genai_model_name())
    response = model.generate_content(prompt)
    return response.text.strip()


def chat_about_resume(resume_text: str, question: str, chat_history: list | None = None) -> str:
    """
    RAG-style chat: answers questions grounded in a specific candidate's
    resume text (retrieved via rag.get_relevant_context).
    """
    history_text = ""
    if chat_history:
        for turn in chat_history[-6:]:  # keep last few turns for context
            role = turn.get("role", "user")
            content = turn.get("content", "")
            history_text += f"{role.upper()}: {content}\n"

    prompt = f"""You are a hiring assistant. Answer the question ONLY using information
in the resume below. If the answer isn't in the resume, say so honestly instead of guessing.

RESUME:
{resume_text[:10000]}

CONVERSATION SO FAR:
{history_text}

QUESTION:
{question}

Answer concisely."""

    model = genai.GenerativeModel(genai_model_name())
    response = model.generate_content(prompt)
    return response.text.strip()


def genai_model_name() -> str:
    import os

    return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
