import streamlit as st
import PyPDF2
import re

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Resume Matcher", layout="wide")

# ---------- STYLING ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #e0f2fe);
    color: #0f172a;
}

.card {
    padding: 20px;
    border-radius: 14px;
    background: white;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-5px);
}

.stButton>button {
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

h1 { color: #1e293b; }
h2, h3 { color: #2563eb; }

.stProgress > div > div > div {
    background-color: #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="card">
    <h1>🚀 AI Resume Matcher</h1>
    <p>✨ Smartly analyze your resume & match it with job descriptions</p>
</div>
""", unsafe_allow_html=True)

# ---------- INPUT ----------
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("📄 Upload Resume (PDF)")

with col2:
    job_desc = st.text_area("💼 Paste Job Description")

# ---------- SAFE PDF READER ----------
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

# ---------- CLEAN TEXT ----------
def clean_text(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    stopwords = {
        "the","and","for","with","you","are","this","that","have","your",
        "from","they","will","their","been","was","were","has","had",
        "but","not","all","can","any","our","out","use","job","role"
    }

    return set([w for w in words if w not in stopwords])

# ---------- ANALYSIS ----------
def analyze(resume_text, job_desc):
    resume_words = clean_text(resume_text)
    job_words = clean_text(job_desc)

    matched = resume_words.intersection(job_words)
    missing = job_words - resume_words

    keyword_score = int((len(matched) / len(job_words)) * 100) if job_words else 0

    # SAFE SCORE FIX
    experience_score = max(0, min(100, keyword_score - 10))
    overall_score = max(0, min(100, int((keyword_score + experience_score) / 2)))

    # FIT CATEGORY
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

# ---------- BUTTON ----------
if st.button("🔍 Analyze Resume"):

    if resume_file is None:
        st.warning("⚠️ Please upload a resume first")

    elif not job_desc.strip():
        st.warning("⚠️ Please enter job description")

    else:
        with st.spinner("Analyzing your resume... ⏳"):
            resume_text = read_pdf(resume_file)
            result = analyze(resume_text, job_desc)

        # SAFE PROGRESS
        progress_value = max(0.0, min(1.0, result["overall_score"] / 100))

        st.markdown("## 📊 Overall Match Score")
        st.progress(progress_value)
        st.markdown(f"### {result['overall_score']}%")
        st.markdown(f"### {result['fit']}")

        # BREAKDOWN
        st.markdown("## 📈 Score Breakdown")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("🧠 Keyword Match", f"{result['keyword_score']}%")

        with col2:
            st.metric("💼 Experience Match", f"{result['experience_score']}%")

        # SKILLS
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### ✅ Matched Skills")
            st.write(", ".join(result["matched"]) or "None")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### ❌ Missing Skills")
            st.write(", ".join(result["missing"]) or "None")
            st.markdown('</div>', unsafe_allow_html=True)

        # SUGGESTIONS
        st.markdown("## 💡 Suggested Skills to Add")
        for skill in result["missing"]:
            st.write(f"👉 {skill}")

        st.success("Analysis Complete ✅")