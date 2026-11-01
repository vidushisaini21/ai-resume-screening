import streamlit as st

from screening import (ALL_SKILLS, DEFAULT_WEIGHTS, EDU_REQ, extract_skills,
                       get_model, read_file, score_candidates)

st.set_page_config(
    page_title="AI Resume Screener | Smart Hiring",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
    }

    /* ── Background ── */
    .stApp {
        background-color: #0d1117;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #21262d;
    }
    [data-testid="stSidebar"] label {
        color: #8b949e !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #c9d1d9 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #e6edf3 !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #21262d !important;
    }

    /* Slider track */
    [data-testid="stSlider"] > div > div > div {
        background: #30363d !important;
    }
    [data-testid="stSlider"] > div > div > div > div {
        background: #58a6ff !important;
    }

    /* ── Top nav bar strip ── */
    .top-bar {
        background-color: #161b22;
        border-bottom: 1px solid #21262d;
        padding: 0.9rem 1.8rem;
        margin: -1rem -1rem 1.5rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .top-bar-brand {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .top-bar-logo {
        width: 32px;
        height: 32px;
        background: #58a6ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }
    .top-bar-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e6edf3;
        letter-spacing: -0.3px;
    }
    .top-bar-tag {
        font-size: 0.7rem;
        background: #1f6feb33;
        border: 1px solid #1f6feb;
        color: #58a6ff;
        border-radius: 4px;
        padding: 0.1rem 0.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ── Page title block ── */
    .page-title {
        margin: 0.5rem 0 0.3rem;
        font-size: 1.9rem;
        font-weight: 800;
        color: #e6edf3;
        letter-spacing: -0.5px;
    }
    .page-sub {
        font-size: 1rem;
        color: #8b949e;
        margin-bottom: 1.8rem;
        line-height: 1.5;
    }

    /* ── Cards ── */
    .card {
        background-color: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 0.8rem;
    }
    .card-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .card-step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        background: #58a6ff;
        color: #0d1117;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 800;
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e6edf3;
    }

    /* ── Metric tiles ── */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin: 1.4rem 0;
    }
    .metric-box {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
    }
    .metric-box .m-label {
        font-size: 0.75rem;
        color: #8b949e;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.4rem;
    }
    .metric-box .m-value {
        font-size: 2rem;
        font-weight: 800;
        color: #e6edf3;
        line-height: 1;
    }
    .metric-box .m-sub {
        font-size: 0.82rem;
        margin-top: 0.25rem;
    }
    .m-blue  .m-value { color: #58a6ff; }
    .m-green .m-value { color: #3fb950; }
    .m-amber .m-value { color: #d29922; }
    .m-purple .m-value { color: #bc8cff; }
    .m-blue  { border-left: 3px solid #58a6ff; }
    .m-green { border-left: 3px solid #3fb950; }
    .m-amber { border-left: 3px solid #d29922; }
    .m-purple { border-left: 3px solid #bc8cff; }

    /* ── Candidate rows ── */
    .cand-row {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 8px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.55rem;
        display: flex;
        align-items: center;
        gap: 1.1rem;
        transition: border-color 0.18s ease, background 0.18s ease;
    }
    .cand-row:hover {
        border-color: #58a6ff;
        background: #1c2230;
    }
    .cand-rank {
        font-size: 1.15rem;
        font-weight: 800;
        color: #58a6ff;
        min-width: 32px;
    }
    .cand-info { flex: 1; }
    .cand-name {
        font-size: 1rem;
        font-weight: 600;
        color: #e6edf3;
    }
    .cand-meta {
        font-size: 0.85rem;
        color: #8b949e;
        margin-top: 0.1rem;
    }
    .cand-right { text-align: right; }
    .cand-score {
        font-size: 1.6rem;
        font-weight: 800;
        color: #e6edf3;
    }
    .cand-bar {
        width: 120px;
        height: 5px;
        background: #21262d;
        border-radius: 3px;
        overflow: hidden;
        margin: 0.35rem 0;
    }
    .cand-bar-fill { height: 100%; border-radius: 3px; }
    .fill-strong   { background: #3fb950; }
    .fill-moderate { background: #d29922; }
    .fill-weak     { background: #f85149; }

    /* ── Badges ── */
    .badge {
        display: inline-block;
        border-radius: 4px;
        padding: 0.15rem 0.55rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-strong   { background: #1a3c2a; color: #3fb950; border: 1px solid #238636; }
    .badge-moderate { background: #2d2208; color: #d29922; border: 1px solid #9e6a03; }
    .badge-weak     { background: #3c1a1a; color: #f85149; border: 1px solid #da3633; }

    /* ── Upload pill ── */
    .upload-pill {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 0.65rem 1rem;
        margin-top: 0.6rem;
        color: #93c5fd;
        font-size: 0.92rem;
        font-weight: 500;
    }

    /* ── Streamlit overrides ── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: #238636 !important;
        color: #ffffff !important;
        border: 1px solid #2ea043 !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.8rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: background 0.18s ease !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: #2ea043 !important;
    }
    .stTextArea textarea {
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #c9d1d9 !important;
        font-size: 0.97rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 2px rgba(88,166,255,0.15) !important;
    }
    .stTextArea label { color: #8b949e !important; font-size: 0.9rem !important; }
    .stFileUploader {
        background: #0d1117 !important;
        border: 1px dashed #30363d !important;
        border-radius: 10px !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background: #1f6feb33 !important;
        border: 1px solid #1f6feb !important;
        color: #58a6ff !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
    }
    .stMultiSelect label, .stSelectbox label { color: #8b949e !important; font-size: 0.9rem !important; }
    div[data-testid="stExpander"] {
        background: #161b22 !important;
        border: 1px solid #21262d !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] summary span {
        color: #c9d1d9 !important;
        font-size: 0.95rem !important;
    }
    .stDownloadButton > button {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #58a6ff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: border-color 0.18s ease !important;
    }
    .stDownloadButton > button:hover {
        border-color: #58a6ff !important;
        background: #1c2230 !important;
    }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    h4 { color: #e6edf3 !important; font-size: 1.05rem !important; }

    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }

    /* ── Divider ── */
    .divider {
        border: none;
        border-top: 1px solid #21262d;
        margin: 2rem 0;
    }

    /* ── Filter Bar ── */
    .filter-bar {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 1.1rem 1.5rem;
        margin: 1.2rem 0 0.5rem;
    }
    .filter-bar-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* ── Footer ── */
    .page-footer {
        text-align: center;
        padding: 2rem 0 0.5rem;
        font-size: 0.85rem;
        color: #484f58;
    }

    /* ── Section header ── */
    .section-header {
        font-size: 1rem;
        font-weight: 700;
        color: #e6edf3;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Model ───────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading language model…")
def load_model():
    return get_model()

load_model()

# ─── Top bar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div class="top-bar-brand">
        <div class="top-bar-logo">📋</div>
        <span class="top-bar-name">ResumeAI</span>
    </div>
    <span style="font-size:0.82rem; color:#484f58;">Smart Hiring · Powered by Sentence-BERT</span>
</div>
""", unsafe_allow_html=True)

# ─── Page title ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-title">Resume Screening & Shortlisting</div>
<div class="page-sub">Paste a job description, upload resumes — AI ranks candidates by fit.</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    st.markdown("**Screening Options**")
    blind = st.checkbox("Blind screening", help="Masks PII; hides file names.")

    st.markdown("---")
    st.markdown("**Score Weights**")
    labels = {
        "semantic":   "Semantic Relevance",
        "skills":     "Skill Match",
        "experience": "Experience",
        "education":  "Education",
        "extras":     "Extras (Certs / Awards)",
    }
    weights = {k: st.slider(labels[k], 0, 100, int(v * 100))
               for k, v in DEFAULT_WEIGHTS.items()}

    st.markdown("""
    <div style="margin-top:1.5rem; padding:0.8rem; background:#0d1117;
         border:1px solid #21262d; border-radius:8px;
         font-size:0.8rem; color:#484f58; line-height:1.6;">
        ℹ️ This is a decision-support tool.<br>
        Human review is always required.
    </div>
    """, unsafe_allow_html=True)

# ─── Inputs ──────────────────────────────────────────────────────────────────
col_jd, col_up = st.columns(2, gap="large")

with col_jd:
    st.markdown("""
    <div class="card">
        <div class="card-label"><span class="card-step-num">1</span> Job Description</div>
        <div class="card-title">Paste the role details below</div>
    </div>
    """, unsafe_allow_html=True)
    jd = st.text_area("Job description", height=220,
                       placeholder="e.g. We are looking for a Python developer with 3+ years of experience…",
                       label_visibility="collapsed")
    detected = sorted(extract_skills(jd)) if jd else []
    must = st.multiselect("Must-have skills (auto-detected)", ALL_SKILLS, default=detected)
    nice = st.multiselect("Nice-to-have skills", ALL_SKILLS)

with col_up:
    st.markdown("""
    <div class="card">
        <div class="card-label"><span class="card-step-num">2</span> Resumes</div>
        <div class="card-title">Upload PDF / DOCX / TXT files</div>
    </div>
    """, unsafe_allow_html=True)
    files = st.file_uploader("Upload files", type=["pdf", "docx", "txt"],
                             accept_multiple_files=True, label_visibility="collapsed")
    if files:
        st.markdown(f"""
        <div class="upload-pill">
            📎 {len(files)} file{'s' if len(files) > 1 else ''} ready
        </div>
        """, unsafe_allow_html=True)

# ─── Filter Bar ──────────────────────────────────────────────────────────────
st.markdown('<div class="filter-bar"><div class="filter-bar-title">🎯 Screening Filters</div></div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([2, 2, 1, 1], gap="medium")
with f1:
    min_years = st.slider("📅 Minimum Experience (years)", 0, 15, 0)
with f2:
    min_edu = st.selectbox("🎓 Minimum Qualification", list(EDU_REQ), index=0)
with f3:
    top_n = st.number_input("👥 Top N Results", 1, 500, 10)
with f4:
    st.markdown("<br>", unsafe_allow_html=True)
    show_only_strong = st.checkbox("Strong matches only", value=False)

# ─── Run button ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    clicked = st.button("▶  Rank Candidates", type="primary",
                        disabled=not (jd and jd.strip() and files),
                        use_container_width=True)

if clicked:
    names, texts = [], []
    for f in files:
        try:
            t = read_file(f.name, f.getvalue())
        except Exception as e:
            st.warning(f"Could not read **{f.name}**: {e}")
            continue
        if t.strip():
            names.append(f.name)
            texts.append(t)
        else:
            st.warning(f"No text in **{f.name}** — scanned PDF?")
    if texts:
        with st.spinner("Scoring candidates…"):
            st.session_state["results"] = score_candidates(
                texts, jd, names=names, must=must, nice=nice,
                min_years=min_years, min_education=min_edu,
                weights=weights, blind=blind)

# ─── Results ─────────────────────────────────────────────────────────────────
df = st.session_state.get("results")
if df is not None:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    strong   = int((df["match"] == "Strong Match").sum())
    moderate = int((df["match"] == "Moderate Match").sum())
    avg      = df["final_score"].mean()
    shown    = df.head(int(top_n))
    if show_only_strong:
        shown = shown[shown["match"] == "Strong Match"]

    # Metrics
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-box m-blue">
            <div class="m-label">Screened</div>
            <div class="m-value">{len(df)}</div>
            <div class="m-sub" style="color:#8b949e;">candidates total</div>
        </div>
        <div class="metric-box m-green">
            <div class="m-label">Strong Match</div>
            <div class="m-value">{strong}</div>
            <div class="m-sub" style="color:#3fb950;">score ≥ 75</div>
        </div>
        <div class="metric-box m-amber">
            <div class="m-label">Moderate</div>
            <div class="m-value">{moderate}</div>
            <div class="m-sub" style="color:#d29922;">score 50–74</div>
        </div>
        <div class="metric-box m-purple">
            <div class="m-label">Avg Score</div>
            <div class="m-value">{avg:.1f}</div>
            <div class="m-sub" style="color:#8b949e;">out of 100</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Candidate rows
    st.markdown('<div class="section-header">🏅 Ranked Candidates</div>', unsafe_allow_html=True)
    for idx, row in shown.iterrows():
        match = row["match"]
        score = row["final_score"]
        matched = row["matched_skills"] or "—"

        badge_cls = ("badge-strong"   if match == "Strong Match"   else
                     "badge-moderate" if match == "Moderate Match" else "badge-weak")
        fill_cls  = ("fill-strong"    if match == "Strong Match"   else
                     "fill-moderate"  if match == "Moderate Match" else "fill-weak")

        st.markdown(f"""
        <div class="cand-row">
            <div class="cand-rank">#{idx+1}</div>
            <div class="cand-info">
                <div class="cand-name">{row['candidate']}</div>
                <div class="cand-meta">🛠 {matched} &nbsp;·&nbsp; 📅 {row['years_exp']:.0f} yrs</div>
            </div>
            <div class="cand-right">
                <div class="cand-score">{score}</div>
                <span class="badge {badge_cls}">{match}</span>
                <div class="cand-bar">
                    <div class="cand-bar-fill {fill_cls}" style="width:{min(score,100)}%"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart
    st.markdown('<div class="section-header">📈 Score Distribution</div>', unsafe_allow_html=True)
    st.bar_chart(shown.set_index("candidate")["final_score"], color="#58a6ff")

    # Breakdown
    with st.expander("🔍 Component Score Breakdown (0 – 1 each)"):
        st.dataframe(
            shown[["candidate", "semantic", "skills", "experience", "education", "extras"]],
            hide_index=True, use_container_width=True)

    # Missing skills
    with st.expander("⚠️ Missing Skills Per Candidate"):
        for _, row in shown.iterrows():
            if row["missing_skills"]:
                st.markdown(f"**{row['candidate']}** — `{row['missing_skills']}`")
            else:
                st.markdown(f"**{row['candidate']}** — ✅ All required skills present")

    # Download
    st.markdown("<br>", unsafe_allow_html=True)
    _, dl_col, _ = st.columns([1, 2, 1])
    with dl_col:
        st.download_button("⬇  Download CSV", shown.to_csv(index=False).encode(),
                           file_name="shortlist.csv", mime="text/csv",
                           use_container_width=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-footer">
    ResumeAI &nbsp;·&nbsp; Sentence-BERT + Streamlit &nbsp;·&nbsp; Built for smarter hiring
</div>
""", unsafe_allow_html=True)
