from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import uuid
from datetime import datetime
import httpx
import PyPDF2
from docx import Document
import google.generativeai as genai
import os
import json

import storage
import database
import rag
import genai_features

app = FastAPI(title="Jetski SmartHire API", version="2.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# Choose model (options: gemini-1.5-flash, gemini-1.5-pro, gemini-pro)
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
model = genai.GenerativeModel(model_name)

# Screening results are now persisted via database.py (Firestore in
# production, in-memory fallback for local dev) instead of a plain dict.
# Uploaded resume files are persisted via storage.py (Google Cloud
# Storage in production, local disk fallback for local dev).


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        from io import BytesIO
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return ""


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from Word document"""
    try:
        from io import BytesIO
        doc = Document(BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return ""


async def analyze_resume_with_gemini(
    resume_text: str, 
    job_description: str
) -> dict:
    """Analyze resume using Google Gemini AI"""
    
    prompt = f"""Analyze the following resume against the job description and provide a detailed screening assessment.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a JSON response with the following structure (ONLY JSON, no other text):
{{
  "score": 0-100,
  "match_percentage": 0-100,
  "status": "passed" | "failed" | "pending",
  "feedback": "Detailed feedback about the candidate",
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2"]
}}

Scoring criteria:
- Score 80-100: Excellent match, candidate meets most key requirements
- Score 60-79: Good match, candidate meets some key requirements  
- Score 40-59: Partial match, candidate needs development in key areas
- Score below 40: Poor match, significant gaps in qualifications

Be specific and professional in your assessment."""

    try:
        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse JSON response
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            raise ValueError("No JSON found in response")
            
    except Exception as e:
        print(f"Error analyzing resume with Gemini: {str(e)}")
        return {
            "score": 0,
            "match_percentage": 0,
            "status": "failed",
            "feedback": f"Error processing resume: {str(e)}",
            "strengths": [],
            "improvements": ["Unable to process resume"]
        }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Jetski SmartHire API",
        "version": "2.0.0"
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/screen")
async def screen_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Screen a resume against a job description"""
    
    try:
        # Validate inputs
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="No job description provided")
        
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload PDF or Word document"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        if file.content_type == "application/pdf":
            resume_text = extract_text_from_pdf(file_content)
        elif file.content_type in [
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            resume_text = extract_text_from_docx(file_content)
        else:
            raise HTTPException(status_code=400, detail="Unable to extract text from file")
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Resume file appears to be empty")
        
        # Analyze with Gemini
        analysis = await analyze_resume_with_gemini(resume_text, job_description)

        # Persist the raw file to cloud storage (GCS, or local disk in dev)
        storage_ref = storage.save_resume_file(file_content, file.filename)

        # Embed the resume text so it becomes searchable via RAG later
        try:
            embedding = rag.embed_text(resume_text)
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            embedding = []

        # Create result object
        result_id = str(uuid.uuid4())
        result = {
            "id": result_id,
            "filename": file.filename,
            "score": analysis.get("score", 0),
            "match_percentage": analysis.get("match_percentage", 0),
            "status": analysis.get("status", "pending"),
            "feedback": analysis.get("feedback", ""),
            "strengths": analysis.get("strengths", []),
            "improvements": analysis.get("improvements", []),
            "timestamp": datetime.utcnow().isoformat(),
            "storage_ref": storage_ref,
            "job_description": job_description,
            "resume_text": resume_text,
            "embedding": embedding,
        }

        # Persist result (Firestore in production, in-memory in dev)
        database.save_result(result_id, result)

        # Don't send the full resume text / embedding back over the wire
        response_result = {k: v for k, v in result.items() if k not in ("resume_text", "embedding")}
        return response_result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error screening resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error screening resume: {str(e)}")


def _strip_internal_fields(result: dict) -> dict:
    return {k: v for k, v in result.items() if k not in ("resume_text", "embedding")}


@app.get("/api/results")
async def get_results():
    """Get all screening results"""
    return [_strip_internal_fields(r) for r in database.list_results()]


@app.get("/api/results/{result_id}")
async def get_result(result_id: str):
    """Get specific screening result"""
    result = database.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return _strip_internal_fields(result)


@app.delete("/api/results/{result_id}")
async def delete_result(result_id: str):
    """Delete screening result"""
    deleted = database.delete_result(result_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"status": "deleted"}


@app.post("/api/stats")
async def get_stats():
    """Get screening statistics"""
    results = database.list_results()
    
    if not results:
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "average_score": 0
        }
    
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    
    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "average_score": round(avg_score, 2)
    }


# =========================================================
# RAG + GenAI endpoints
# =========================================================

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class CoverLetterRequest(BaseModel):
    result_id: str
    tone: str = "professional"


class ImproveResumeRequest(BaseModel):
    result_id: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    result_id: str
    question: str
    history: list[ChatMessage] = []


@app.get("/api/system-info")
async def system_info():
    """Report which cloud backends are active (useful for verifying deployment config)"""
    return {
        "storage_backend": storage.storage_backend_name(),
        "database_backend": database.database_backend_name(),
        "gemini_model": model_name,
        "embedding_model": rag.EMBEDDING_MODEL,
    }


@app.post("/api/search")
async def semantic_search(request: SearchRequest):
    """
    RAG-powered semantic search across all previously screened resumes.
    Example query: "candidates with backend Python and AWS experience"
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        matches = rag.semantic_search(request.query, top_k=request.top_k)
        return {"query": request.query, "results": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running semantic search: {str(e)}")


@app.post("/api/cover-letter")
async def cover_letter(request: CoverLetterRequest):
    """Generate a tailored cover letter for a previously screened candidate"""
    result = database.get_result(request.result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    try:
        letter = genai_features.generate_cover_letter(
            resume_text=result.get("resume_text", ""),
            job_description=result.get("job_description", ""),
            tone=request.tone,
        )
        return {"result_id": request.result_id, "cover_letter": letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")


@app.post("/api/improve-resume")
async def improve_resume(request: ImproveResumeRequest):
    """Get GenAI suggestions for improving a candidate's resume"""
    result = database.get_result(request.result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    try:
        suggestions = genai_features.suggest_resume_improvements(
            resume_text=result.get("resume_text", ""),
            job_description=result.get("job_description", ""),
        )
        return {"result_id": request.result_id, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")


@app.post("/api/chat")
async def chat_about_resume(request: ChatRequest):
    """
    RAG-grounded Q&A about a specific candidate, e.g.
    "Does this candidate have Kubernetes experience?"
    """
    context = rag.get_relevant_context(request.result_id)
    if not context:
        raise HTTPException(status_code=404, detail="Result not found or has no stored resume text")

    try:
        answer = genai_features.chat_about_resume(
            resume_text=context,
            question=request.question,
            chat_history=[m.dict() for m in request.history],
        )
        return {"result_id": request.result_id, "question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
