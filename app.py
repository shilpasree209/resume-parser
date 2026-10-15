import streamlit as st
from utils import extract_text_from_file, parse_resume_with_gemini

st.set_page_config(page_title="Resume Auto-Fill App", layout="wide")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY is missing! Please configure it in your Streamlit secrets.")
    st.stop()

st.title("📄 AI Resume Parser & Auto-Fill Form")
st.markdown("Upload a resume (`.pdf` or `.docx`) to automatically populate the application form below.")

# Input for Google API Key (or you can load it from st.secrets)
# api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Get a free key from aistudio.google.com")

# Initialize session state keys for form fields if they don't exist
default_fields = {
    "full_name": "",
    "email": "",
    "phone": "",
    "summary": "",
    "skills": "",
    "exp_title": "",
    "exp_company": ""
}

for key, val in default_fields.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- UPLOAD SECTION ---
st.subheader("1. Upload Resume")
uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

if uploaded_file is not None:
    if st.button("Extract & Auto-Fill", type="primary"):
        if not api_key:
            st.warning("Please enter your Gemini API key in the sidebar first.")
        else:
            with st.spinner("Reading resume and extracting details with Gemini..."):
                try:
                    # Extract raw text
                    raw_text = extract_text_from_file(uploaded_file)
                    
                    # Parse using Gemini structured output
                    extracted_data = parse_resume_with_gemini(raw_text, api_key)
                    
                    # Map extracted data to session state variables
                    st.session_state["full_name"] = extracted_data.full_name
                    st.session_state["email"] = extracted_data.email
                    st.session_state["phone"] = extracted_data.phone
                    st.session_state["summary"] = extracted_data.summary or ""
                    st.session_state["skills"] = ", ".join(extracted_data.skills)
                    st.session_state["exp_title"] = extracted_data.experience_title or ""
                    st.session_state["exp_company"] = extracted_data.experience_company or ""
                    
                    st.success("Resume parsed successfully! Form fields have been auto-filled.")
                except Exception as e:
                    st.error(f"Error parsing resume: {e}")

# --- MAIN AUTO-FILLED FORM ---
st.markdown("---")
st.subheader("2. Application Form")

with st.form("resume_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name", value=st.session_state["full_name"])
        email = st.text_input("Email", value=st.session_state["email"])
        phone = st.text_input("Phone", value=st.session_state["phone"])
    
    with col2:
        exp_title = st.text_input("Most Recent Job Title", value=st.session_state["exp_title"])
        exp_company = st.text_input("Most Recent Company", value=st.session_state["exp_company"])
        skills = st.text_input("Skills (comma-separated)", value=st.session_state["skills"])

    summary = st.text_area("Professional Summary", value=st.session_state["summary"])
    
    submitted = st.form_submit_button("Submit Application")
    if submitted:
        st.balloons()
        st.success("Form submitted successfully!")
        st.json({
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "job_title": exp_title,
            "company": exp_company,
            "skills": skills,
            "summary": summary
        })