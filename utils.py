import json
import logging
import random
import time
from pydantic import BaseModel, Field
from typing import List, Optional
import pdfplumber
from docx import Document
from groq import Groq
from groq import APIError as GroqAPIError

logger = logging.getLogger(__name__)


class ResumeSchema(BaseModel):
    full_name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    summary: Optional[str] = Field(default=None, description="Professional summary or objective")
    skills: List[str] = Field(description="List of technical and soft skills")
    experience_title: Optional[str] = Field(default=None, description="Most recent job title")
    experience_company: Optional[str] = Field(default=None, description="Most recent company name")


# Build the JSON schema string once so prompts stay consistent
_SCHEMA_HINT = json.dumps(ResumeSchema.model_json_schema(), indent=2)

_SYSTEM_PROMPT = (
    "You are a resume parser. Extract candidate information from the resume "
    "and return ONLY valid JSON matching this schema — no markdown, no explanation:\n\n"
    f"{_SCHEMA_HINT}\n\n"
    "Rules:\n"
    "- Use empty strings for missing required string fields.\n"
    "- Use empty lists for missing required list fields.\n"
    "- Use null for missing optional fields."
)


def extract_text_from_file(uploaded_file) -> str:
    """Extracts raw text from PDF or DOCX files."""
    if uploaded_file.type == "application/pdf":
        pages = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
        text = "\n".join(pages)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        table_rows = [
            " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            for table in doc.tables
            for row in table.rows
        ]
        text = "\n".join(paragraphs + [row for row in table_rows if row])
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX resume.")

    if not text.strip():
        raise ValueError(
            "No readable text was found in the resume. If this is a scanned PDF, "
            "use a text-based PDF or DOCX file."
        )

    return text


def parse_resume(raw_text: str, groq_api_key: str) -> ResumeSchema:
    """Uses Groq (free tier) to parse a resume into structured data."""
    if not raw_text.strip():
        raise ValueError("The resume contains no readable text to parse.")

    client = Groq(api_key=groq_api_key)

    max_retries = 4
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": raw_text},
                ],
                temperature=0.1,
                max_tokens=2048,
            )
            break
        except GroqAPIError as error:
            status_code = getattr(error, "status_code", None)
            if status_code not in (429, 503) or attempt == max_retries:
                raise

            delay = min(2 ** attempt, 8) + random.uniform(0, 0.25)
            logger.warning(
                "Groq returned HTTP %s; retrying in %.2f seconds "
                "(retry %d/%d).",
                status_code,
                delay,
                attempt + 1,
                max_retries,
            )
            time.sleep(delay)

    reply = response.choices[0].message.content
    if not reply:
        raise ValueError("Groq returned an empty response for this resume.")

    # Strip markdown fences if the model wraps the JSON
    cleaned = reply.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]  # drop ```json line
        cleaned = cleaned.rsplit("```", 1)[0]  # drop closing ```

    return ResumeSchema.model_validate_json(cleaned)