import os
import re
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from anakin import Anakin

load_dotenv()

st.set_page_config(
    page_title="AgentScout | Anakin Forge",
    page_icon="🧭",
    layout="wide",
)

st.markdown("""
<style>
.main {max-width: 1200px;}
.hero {
    padding: 24px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111827, #312e81);
    color: white;
    margin-bottom: 24px;
}
.job-card {
    padding: 18px;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    margin: 12px 0;
    background: white;
}
.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    background: #eef2ff;
    margin-right: 6px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🧭 AgentScout</h1>
<p>Autonomous AI job research agent powered by Anakin.</p>
<p>It searches live web information, reads the returned evidence, scores opportunities against your requirements, and turns the results into an actionable shortlist.</p>
</div>
""", unsafe_allow_html=True)

api_key = os.getenv("ANAKIN_API_KEY")

if not api_key:
    st.warning("ANAKIN_API_KEY is not configured. Add it as an environment variable before running the agent.")
    st.info("For local testing, create a .env file containing: ANAKIN_API_KEY=your_key")
    st.stop()

client = Anakin(api_key=api_key, timeout=60.0, max_retries=3)

with st.sidebar:
    st.header("🎯 Your requirements")
    role = st.text_input("Target role", "Data Analyst")
    location = st.text_input("Location", "India")
    skills = st.text_input("Important skills", "SQL, Excel, Power BI, Python")
    work_mode = st.selectbox("Work mode", ["Any", "Remote", "Hybrid", "On-site"])
    experience = st.selectbox("Experience", ["Fresher / 0-1 years", "1-2 years", "2-3 years"])
    max_results = st.slider("Number of web results", 3, 10, 6)
    run = st.button("🚀 Run Agent", use_container_width=True)

def get_value(obj, key, default=""):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()

def score_result(result, requirements):
    text = " ".join([
        clean_text(get_value(result, "title")),
        clean_text(get_value(result, "snippet")),
        clean_text(get_value(result, "content")),
        clean_text(get_value(result, "url")),
    ]).lower()

    score = 0
    reasons = []

    role_words = [w for w in re.findall(r"[a-zA-Z0-9+#.]+", requirements["role"].lower()) if len(w) > 2]
    skill_words = [w.strip().lower() for w in requirements["skills"].split(",") if w.strip()]

    role_hits = sum(1 for w in role_words if w in text)
    skill_hits = sum(1 for w in skill_words if w in text)

    score += min(role_hits * 15, 40)
    score += min(skill_hits * 8, 32)

    if requirements["location"].lower() in text or requirements["location"].lower() == "any":
        score += 12
        reasons.append("Location preference appears relevant.")
    if requirements["work_mode"].lower() == "any" or requirements["work_mode"].lower() in text:
        score += 8
        reasons.append("Work-mode preference appears relevant.")
    if "fresher" in requirements["experience"].lower() and any(x in text for x in ["fresher", "entry level", "0-1", "0 to 1", "graduate"]):
        score += 8
        reasons.append("The listing appears suitable for an early-career applicant.")

    if role_hits:
        reasons.append(f"Role keywords matched: {role_hits}")
    if skill_hits:
        reasons.append(f"Skill keywords matched: {skill_hits}")

    return min(score, 100), reasons

def make_search_prompt():
    return f"""
You are the web-research component of an autonomous job discovery agent.

Find current job opportunities matching:
- Target role: {role}
- Location: {location}
- Experience: {experience}
- Skills: {skills}
- Work mode: {work_mode}

Search the live web and prioritize actual job postings, company career pages, and reputable job boards.
Return results that contain useful details such as job title, company, location, experience, skills, application URL, and any salary information available.

Avoid generic career advice and avoid fabricated jobs.
The purpose is to help an applicant decide which opportunities deserve an application first.
""".strip()

if run:
    with st.spinner("🤖 Agent is researching the live web with Anakin..."):
        try:
            search_result = client.search(make_search_prompt(), limit=max_results)
            raw_results = get_value(search_result, "results", []) or []

            requirements = {
                "role": role,
                "location": location,
                "skills": skills,
                "work_mode": work_mode,
                "experience": experience,
            }

            ranked = []
            for item in raw_results:
                score, reasons = score_result(item, requirements)
                ranked.append({
                    "item": item,
                    "score": score,
                    "reasons": reasons,
                })

            ranked.sort(key=lambda x: x["score"], reverse=True)
            st.session_state["ranked"] = ranked
            st.session_state["requirements"] = requirements

        except Exception as exc:
            st.error("The agent could not complete the research request.")
            st.code(str(exc))
            st.stop()

if "ranked" in st.session_state:
    ranked = st.session_state["ranked"]

    st.subheader("🧠 Agent result")
    st.write(
        f"Found **{len(ranked)}** web result(s), then ranked them against your "
        f"role, skills, location, experience, and work-mode preferences."
    )

    if ranked:
        top = ranked[0]
        st.success(
            f"Top recommendation: {clean_text(get_value(top['item'], 'title')) or 'Untitled result'} "
            f"— match score {top['score']}/100"
        )

    for index, entry in enumerate(ranked, start=1):
        item = entry["item"]
        title = clean_text(get_value(item, "title")) or "Untitled result"
        url = clean_text(get_value(item, "url"))
        snippet = clean_text(get_value(item, "snippet"))
        content = clean_text(get_value(item, "content"))
        text = content or snippet

        domain = urlparse(url).netloc if url else "Web source"

        st.markdown('<div class="job-card">', unsafe_allow_html=True)
        st.markdown(f"### {index}. {title}")
        st.markdown(
            f'<span class="badge">Match: {entry["score"]}/100</span>'
            f'<span class="badge">{domain}</span>',
            unsafe_allow_html=True,
        )

        if text:
            st.write(text[:1000] + ("..." if len(text) > 1000 else ""))

        if entry["reasons"]:
            st.write("**Why it ranked here:**")
            for reason in entry["reasons"]:
                st.write(f"- {reason}")

        if url:
            st.link_button("Open source / application page", url)

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("⚙️ Agent workflow")
    st.markdown("""
    **1. Understand → 2. Research → 3. Read evidence → 4. Score → 5. Recommend → 6. Take action**

    - **Understand:** converts the user's requirements into a research prompt.
    - **Research:** Anakin searches the live web.
    - **Read:** the agent consumes returned web evidence.
    - **Score:** results are evaluated against role, skills, location, experience and work mode.
    - **Recommend:** the strongest opportunities are shown first.
    - **Act:** the user can open the source/application page directly.
    """)

else:
    st.subheader("How to demo it")
    st.markdown("""
    1. Keep the default **Data Analyst** example or change the requirements.
    2. Click **Run Agent**.
    3. Wait for the live web research.
    4. Show the ranked results.
    5. Open one result using **Open source / application page**.
    6. Explain that Anakin performs the web research layer while AgentScout performs the preference-based ranking and action-oriented presentation.
    """)

st.caption("Built for Anakin Forge Hackathon • AgentScout")
