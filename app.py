import streamlit as st
import PyPDF2
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Resume Matcher Pro", layout="wide")

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

# ---------- HEADER ----------
st.markdown("""
<div class="card">
    <h1>🚀 AI Resume Matcher Pro</h1>
    <p>Upload resume → analyze → improve → get job insights</p>
</div>
""", unsafe_allow_html=True)

# ---------- SAMPLE JD ----------
sample_jd = """
Looking for a Python Developer with experience in APIs, SQL, and data analysis.
Should have knowledge of cloud platforms and problem-solving skills.
"""

if st.button("✨ Use Sample Job Description"):
    st.session_state["jd"] = sample_jd

# ---------- INPUT ----------
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("📄 Upload Resume (PDF)")
    resume_text_input = st.text_area("✍️ Or paste resume text (Demo mode)")

with col2:
    job_desc = st.text_area("💼 Paste Job Description", value=st.session_state.get("jd", ""))

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

# ---------- ANALYSIS ----------
def analyze(resume_text, job_desc):
    resume_words = clean_text(resume_text)
    job_words = clean_text(job_desc)

    matched = resume_words.intersection(job_words)
    missing = job_words - resume_words

    keyword_score = int((len(matched) / len(job_words)) * 100) if job_words else 0
    experience_score = max(0, min(100, keyword_score - 10))
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

# ---------- JOB ROLE RECOMMENDER ----------
def recommend_roles(skills):
    roles = []

    if "python" in skills or "data" in skills:
        roles.append("Data Analyst")
    if "sql" in skills:
        roles.append("Database Developer")
    if "api" in skills:
        roles.append("Backend Developer")
    if "cloud" in skills:
        roles.append("Cloud Engineer")

    return roles if roles else ["General Software Engineer"]

# ---------- BULLET GENERATOR ----------
def improve_bullet(text):
    return f"✔ Improved: {text.capitalize()} with measurable impact and action-driven language."

# ---------- PDF ----------
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

# ---------- ANALYZE BUTTON ----------
if st.button("🔍 Analyze Resume"):

    resume_text = ""

    if resume_file:
        resume_text = read_pdf(resume_file)
    elif resume_text_input.strip():
        resume_text = resume_text_input
    else:
        st.warning("⚠️ Upload resume or paste text")
        st.stop()

    if not job_desc.strip():
        st.warning("⚠️ Enter job description")
        st.stop()

    result = analyze(resume_text, job_desc)

    st.progress(result["overall_score"] / 100)
    st.markdown(f"### {result['overall_score']}% - {result['fit']}")

    st.metric("🧠 Keyword Match", f"{result['keyword_score']}%")
    st.metric("💼 Experience Match", f"{result['experience_score']}%")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Matched Skills")
        st.write(result["matched"])

    with col2:
        st.markdown("### ❌ Missing Skills")
        st.write(result["missing"])

    # ---------- JOB ROLES ----------
    st.markdown("## 🎯 Recommended Roles")
    roles = recommend_roles(result["matched"])
    for r in roles:
        st.write(f"👉 {r}")

    # ---------- BULLET GENERATOR ----------
    st.markdown("## ✍️ Improve Resume Bullet")
    user_bullet = st.text_input("Enter your resume bullet")

    if st.button("✨ Improve Bullet"):
        if user_bullet:
            improved = improve_bullet(user_bullet)
            st.success(improved)
        else:
            st.warning("Enter a bullet point")

    # ---------- SUGGESTIONS ----------
    st.markdown("## 💡 Suggestions")
    for skill in result["missing"]:
        st.write(f"👉 Add {skill}")

    # ---------- DOWNLOAD ----------
    pdf = generate_pdf(result)
    st.download_button(
        label="📄 Download Report",
        data=pdf,
        file_name="resume_report.pdf",
        mime="application/pdf"
    )