import streamlit as st
import PyPDF2
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# OPTIONAL AI (safe fallback if not used)
try:
    from openai import OpenAI
    client = OpenAI(api_key="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")  # optional
except:
    client = None

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Resume Matcher", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #e0f2fe);
}
.card {
    padding: 20px;
    border-radius: 14px;
    background: white;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.stButton>button {
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🚀 AI Resume Matcher</h1>
    <p>Smart resume analysis with AI insights</p>
</div>
""", unsafe_allow_html=True)

# ---------- INPUT ----------
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("📄 Upload Resume (PDF)")
with col2:
    job_desc = st.text_area("💼 Paste Job Description")

# ---------- PDF ----------
def read_pdf(file):
    if file is None:
        return ""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
        return text
    except:
        return ""

# ---------- CLEAN ----------
def clean_text(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stopwords = {"the","and","for","with","you","are","this","that","have","your"}
    return set([w for w in words if w not in stopwords])

# ---------- ANALYSIS (WEIGHTED) ----------
def analyze(resume_text, job_desc):
    resume_words = clean_text(resume_text)
    job_words = clean_text(job_desc)

    matched = resume_words.intersection(job_words)
    missing = job_words - resume_words

    keyword_score = int((len(matched) / len(job_words)) * 100) if job_words else 0
    experience_score = max(0, min(100, keyword_score - 10))

    # 🎯 Weighted scoring
    overall_score = int((0.6 * keyword_score) + (0.4 * experience_score))

    if overall_score >= 80:
        fit = "🔥 Strong Match"
    elif overall_score >= 50:
        fit = "⚠️ Moderate Match"
    else:
        fit = "❌ Low Match"

    return {
        "keyword_score": keyword_score,
        "experience_score": experience_score,
        "overall_score": overall_score,
        "fit": fit,
        "matched": list(matched)[:10],
        "missing": list(missing)[:10]
    }

# ---------- AI SUGGESTIONS ----------
def ai_suggestions(resume_text, job_desc):
    if client is None:
        return ["Add more relevant skills", "Improve formatting", "Highlight achievements"]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Suggest 3 improvements for this resume:\n{resume_text}\n\nJob:\n{job_desc}"
            }]
        )
        return response.choices[0].message.content.split("\n")
    except:
        return ["AI suggestion unavailable"]

# ---------- PDF GENERATION ----------
def generate_pdf(result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = [
        Paragraph(f"Match Score: {result['overall_score']}%", styles['Normal']),
        Paragraph(f"Fit: {result['fit']}", styles['Normal']),
        Paragraph(f"Matched Skills: {', '.join(result['matched'])}", styles['Normal']),
        Paragraph(f"Missing Skills: {', '.join(result['missing'])}", styles['Normal'])
    ]

    doc.build(content)
    buffer.seek(0)
    return buffer

# ---------- BUTTON ----------
if st.button("🔍 Analyze Resume"):

    if resume_file is None:
        st.warning("Upload resume")
    elif not job_desc.strip():
        st.warning("Enter job description")
    else:
        resume_text = read_pdf(resume_file)
        result = analyze(resume_text, job_desc)

        st.progress(result["overall_score"] / 100)
        st.markdown(f"### {result['overall_score']}% - {result['fit']}")

        st.metric("Keyword Match", f"{result['keyword_score']}%")
        st.metric("Experience Match", f"{result['experience_score']}%")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ✅ Matched Skills")
            st.write(result["matched"])

        with col2:
            st.markdown("### ❌ Missing Skills")
            st.write(result["missing"])

        # 🤖 AI Suggestions
        st.markdown("## 🤖 AI Suggestions")
        suggestions = ai_suggestions(resume_text, job_desc)
        for s in suggestions:
            st.write(f"👉 {s}")

        # 📄 PDF Download
        pdf = generate_pdf(result)
        st.download_button(
            label="📄 Download Report",
            data=pdf,
            file_name="resume_report.pdf",
            mime="application/pdf"
        )