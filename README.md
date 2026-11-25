# Resume Parser App

A Streamlit app that extracts candidate details from PDF or DOCX resumes and uses the Groq API to fill an application form.
The parser currently requests the `openai/gpt-oss-120b` model.

## Features

- Upload a PDF or DOCX resume.
- Extract selectable PDF text and DOCX paragraphs and tables.
- Parse the candidate's name, email, phone, professional summary, skills, most recent job title, and company into structured data.
- Review and edit the extracted details before submitting the form.
- Retry transient Groq API `429` and `503` errors up to four times with exponential backoff and jitter.

Scanned PDFs without selectable text are not OCR-processed and cannot be parsed.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/) or Python's `py` launcher and `pip`
- A Groq API key

## Configure the Groq API key

The app reads the key from Streamlit secrets. Create `.streamlit\secrets.toml` in the project directory:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

Create a key in the [Groq Console](https://console.groq.com/keys). Keep this file private and do not commit a real API key to source control.

## Run with uv

Open PowerShell in the project directory and run:

```powershell
uv run --with-requirements requirements.txt --python 3.12 python -m streamlit run app.py
```

The command installs the listed dependencies into uv's run environment if needed, then starts Streamlit.

## Run with a virtual environment

If you prefer a project-local virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If the `py` launcher is unavailable, create the environment with `python -m venv .venv` instead.

## Usage

1. Upload a PDF or DOCX resume.
2. Select **Extract & Auto-Fill** and wait for Groq to parse the resume.
3. Review and edit the populated form.
4. Select **Submit Application** to display the form data.

The app currently displays submitted information in the browser; it does not save or send applications to an external service. Resume text is sent to Groq for parsing, so only upload documents you are comfortable processing through that service.
