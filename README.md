# Resume Parser App

A Streamlit app that extracts candidate details from PDF or DOCX resumes and uses the Google Gemini API to fill an application form.

## Features

- Upload a resume in PDF or DOCX format.
- Extract text with `pdfplumber` or `python-docx`.
- Parse the candidate's name, email, phone, professional summary, skills, most recent job title, and company using Gemini structured output.
- Review and edit the extracted details in the application form.
- Display submitted form data in the app.

## Requirements

- Python
- A Google Gemini API key

## Setup

Open PowerShell in the project directory and create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If the `py` launcher is unavailable, use `python` instead:

```powershell
python -m venv .venv
```

## Configure the Gemini API key

The app reads the key from Streamlit secrets. Create `.streamlit\secrets.toml` in the project directory with:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
```

Keep this file private and do not commit a real API key to source control. You can obtain an API key from [Google AI Studio](https://aistudio.google.com/).

## Run

With the virtual environment activated, start the app:

```powershell
streamlit run app.py
```

Streamlit will print a local URL to open in your browser.

## Usage

1. Upload a PDF or DOCX resume.
2. Select **Extract & Auto-Fill** and wait for Gemini to parse the resume.
3. Review and edit the populated form.
4. Select **Submit Application** to display the form data.

The app currently displays submitted information in the browser; it does not save or send applications to an external service. Resume text is sent to Google's Gemini API for parsing, so only upload documents you are comfortable processing through that service.
