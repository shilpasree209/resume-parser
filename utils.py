from time import time
from pydantic import BaseModel, Field
from typing import List, Optional
import pdfplumber
from docx import Document
from google import genai
from google.genai import types

class ResumeSchema(BaseModel):
    full_name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    summary: Optional[str] = Field(description="Professional summary or objective")
    skills: List[str] = Field(description="List of technical and soft skills")
    experience_title: Optional[str] = Field(description="Most recent job title")
    experience_company: Optional[str] = Field(description="Most recent company name")

def extract_text_from_file(uploaded_file) -> str:
    """Extracts raw text from PDF or DOCX files."""
    text = ""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text

def parse_resume_with_gemini(raw_text: str, api_key: str) -> ResumeSchema:
    """Uses Gemini 2.5 Flash with Pydantic structured outputs."""
    client = genai.Client(api_key=api_key)

    # Primary model is gemini-3.8-flash, with reliable fallbacks if throttled
    models_to_try = ['gemini-3.8-flash', 'gemini-1.5-flash']
    
    last_exception = None
    
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"Extract the candidate's profile information from this resume text:\n\n{raw_text}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ResumeSchema,
                        temperature=0.1,
                    ),
                )
                return ResumeSchema.model_validate_json(response.text)
            
            except Exception as e:
                last_exception = e
                error_str = str(e)
                # If it's a 503 high demand error, wait briefly before retrying or switching models
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    # time.sleep(2)
                    continue
                else:
                    raise e
                    
    raise Exception(f"All models failed due to high server demand. Please try again in a moment. Details: {last_exception}")
    
    # response = client.models.generate_content(
    #     model='gemini-3.8-flash',
    #     contents=f"Extract the candidate's profile information from this resume text:\n\n{raw_text}",
    #     config=types.GenerateContentConfig(
    #         response_mime_type="application/json",
    #         response_schema=ResumeSchema,
    #         temperature=0.1,
    #     ),
    # )
    
    # Parse the JSON response back into your Pydantic model
    return ResumeSchema.model_validate_json(response.text)