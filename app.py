"""
app.py - Maple: AI Football Scout Assistant
Main Streamlit application entry point.
"""

import streamlit as st
import pandas as pd
import os
import io
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

# -- Page config (must be first Streamlit call) ------------------------------
st.set_page_config(
    page_title="Maple - AI Football Scout",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Internal imports ---------------------------------------------------------
from src.data_loader import load_cached_dataset, get_dataset_info
from src.query_parser import parse_query
from src.intent_router import route_intent
from src.llm_service import get_groq_client, generate_summary, generate_scout_report
from src.visualization import (
    chart_top_players,
    chart_top_clubs,
    chart_age_vs_overall,
    chart_player_comparison,
    chart_value_players,
    chart_player_radar_single,
    chart_percentile_bars,
)
from src.utils import EXAMPLE_QUERIES, sanitize_query


# -- PDF Export Helper --------------------------------------------------------
def generate_pdf(title: str, table_df=None, summary: str = "", strengths=None, improvements=None, similar=None) -> bytes:
    """Build a ReportLab PDF and return the raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    accent = colors.HexColor("#00D4A4")
    dark   = colors.HexColor("#0A0E1A")

    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=accent, fontSize=18, spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=dark, fontSize=12, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, leading=14, spaceAfter=4)

    story = []
    story.append(Paragraph("⚽ Maple — AI Football Scout Report", h1))
    story.append(Paragraph(title, h2))
    story.append(HRFlowable(width="100%", thickness=1, color=accent))
    story.append(Spacer(1, 0.3*cm))

    if table_df is not None and not table_df.empty:
        story.append(Paragraph("Player Data", h2))
        col_names = list(table_df.columns)
        data = [col_names] + table_df.astype(str).values.tolist()
        tbl = Table(data, repeatRows=1, hAlign="LEFT")
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), accent),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTSIZE",   (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#F5F8FA"), colors.white]),
            ("GRID",       (0,0), (-1,-1), 0.4, colors.lightgrey),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4*cm))

    if strengths:
        story.append(Paragraph("💪 Strengths", h2))
        for s in strengths:
            story.append(Paragraph(f"✔ {s}", body))
        story.append(Spacer(1, 0.2*cm))

    if improvements:
        story.append(Paragraph("🎯 Areas for Improvement", h2))
        for i in improvements:
            story.append(Paragraph(f"• {i}", body))
        story.append(Spacer(1, 0.2*cm))

    if similar:
        story.append(Paragraph("🤝 Similar Players", h2))
        story.append(Paragraph(", ".join(similar), body))
        story.append(Spacer(1, 0.2*cm))

    if summary:
        story.append(Paragraph("🧠 AI Scout Summary", h2))
        story.append(Paragraph(summary.replace("\n", "<br/>"), body))

    doc.build(story)
    return buf.getvalue()



# -- Custom CSS ---------------------------------------------------------------
st.markdown("""
<style>
/* -- Global ------------------------------------------------------------ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0A0E1A 0%, #0D1525 50%, #0A1020 100%);
    color: #E8EDF2;
}

/* -- Header ------------------------------------------------------------ */
.scout-header {
    background: linear-gradient(90deg, rgba(0,212,164,0.15) 0%, rgba(0,133,255,0.1) 100%);
    border: 1px solid rgba(0,212,164,0.3);
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.scout-header h1 {
    font-size: 28px;
    font-weight: 700;
    color: #E8EDF2;
    margin: 0;
    letter-spacing: -0.5px;
}
.scout-header p {
    color: #8899AA;
    margin: 4px 0 0 0;
    font-size: 14px;
}
.badge {
    display: inline-block;
    background: rgba(0,212,164,0.2);
    color: #00D4A4;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(0,212,164,0.4);
    margin-left: 8px;
    vertical-align: middle;
}

/* FIFA 2026 accent badge */
.badge-fifa {
    display: inline-block;
    background: linear-gradient(90deg, #D4000A 0%, #002868 100%);
    color: #fff;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin-left: 6px;
    vertical-align: middle;
    letter-spacing: 0.5px;
}

/* -- Status pills ------------------------------------------------------ */
.status-ok {
    color: #00D4A4;
    font-weight: 600;
    font-size: 13px;
}
.status-err {
    color: #FF6B6B;
    font-weight: 600;
    font-size: 13px;
}

/* -- Chat messages ----------------------------------------------------- */
.chat-user {
    background: rgba(0,133,255,0.12);
    border: 1px solid rgba(0,133,255,0.25);
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
    color: #C8D8E8;
    font-size: 14px;
}
.chat-assistant {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px 12px 12px 4px;
    padding: 16px 20px;
    margin: 8px 0;
    color: #E8EDF2;
    font-size: 14px;
}

/* -- Result title ------------------------------------------------------ */
.result-title {
    font-size: 16px;
    font-weight: 600;
    color: #00D4A4;
    margin: 0 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0,212,164,0.2);
}

/* -- Insights box ------------------------------------------------------ */
.insights-box {
    background: linear-gradient(135deg, rgba(0,212,164,0.08), rgba(0,133,255,0.08));
    border: 1px solid rgba(0,212,164,0.25);
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 16px;
}
.insights-box h4 {
    color: #00D4A4;
    margin: 0 0 10px 0;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.insights-box p {
    color: #B0C4D8;
    font-size: 13px;
    line-height: 1.7;
    margin: 0;
}

/* -- Error box --------------------------------------------------------- */
.error-box {
    background: rgba(255,107,107,0.08);
    border: 1px solid rgba(255,107,107,0.3);
    border-radius: 10px;
    padding: 14px 18px;
    color: #FF9B9B;
    font-size: 14px;
}

/* -- Sidebar ----------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: rgba(10,14,26,0.95);
    border-right: 1px solid rgba(255,255,255,0.07);
}
.sidebar-section {
    margin-bottom: 20px;
}
.sidebar-section h3 {
    color: #00D4A4;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 10px;
    text-align: center;
}
.stat-card .val {
    font-size: 18px;
    font-weight: 700;
    color: #00D4A4;
}
.stat-card .lbl {
    font-size: 10px;
    color: #667788;
    margin-top: 2px;
}
.example-query {
    display: block;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 6px;
    padding: 7px 10px;
    margin: 4px 0;
    color: #8899AA;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
}
.example-query:hover {
    background: rgba(0,212,164,0.1);
    border-color: rgba(0,212,164,0.3);
    color: #00D4A4;
}

/* -- Dataframe --------------------------------------------------------- */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    overflow: hidden;
}

/* -- Input ------------------------------------------------------------- */
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #E8EDF2 !important;
}

/* -- Divider ----------------------------------------------------------- */
hr {
    border-color: rgba(255,255,255,0.07) !important;
}
</style>
""", unsafe_allow_html=True)


# -- Session state -----------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "dataset_error" not in st.session_state:
    st.session_state.dataset_error = None
if "dataset_source" not in st.session_state:
    st.session_state.dataset_source = None   # None | "sample" | uploaded filename
if "data_choice" not in st.session_state:
    st.session_state.data_choice = None      # tracks the radio selection

df: pd.DataFrame | None = st.session_state.df
groq_client = get_groq_client()


# -- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 24px 0;">
        <div style="font-size:44px">⚽</div>
        <div style="font-size:16px;font-weight:700;color:#E8EDF2;margin-top:6px;">Maple</div>
        <div style="font-size:11px;color:#556677;margin-top:2px;">Your AI Football Scout</div>
        <div style="margin-top:8px;">
            <span class="badge-fifa">FIFA World Cup 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -- Dataset source selector ---------------------------------------------
    st.markdown('<div class="sidebar-section"><h3>📂 Data Source</h3>', unsafe_allow_html=True)

    data_choice = st.radio(
        "Choose your dataset",
        options=["📦 Use sample dataset", "⬆️ Upload CSV"],
        index=0 if st.session_state.data_choice in (None, "sample") else 1,
        label_visibility="collapsed",
        key="data_source_radio",
    )

    # Detect if the user switched choice — reset dataset
    choice_key = "sample" if "sample" in data_choice else "upload"
    if choice_key != st.session_state.data_choice:
        st.session_state.data_choice = choice_key
        st.session_state.df = None
        st.session_state.dataset_error = None
        st.session_state.dataset_source = None
        st.session_state.messages = []
        st.rerun()

    # -- Branch: sample dataset ----------------------------------------------
    if choice_key == "sample":
        if st.session_state.df is None and st.session_state.dataset_error is None:
            try:
                with st.spinner("Loading sample dataset..."):
                    st.session_state.df = load_cached_dataset("data/fifa_players.csv")
                    st.session_state.dataset_source = "sample"
            except Exception as e:
                st.session_state.dataset_error = str(e)

    # -- Branch: upload CSV --------------------------------------------------
    else:
        import io
        from src.data_loader import load_dataset

        uploaded_file = st.file_uploader(
            "Drop your FIFA CSV here",
            type=["csv"],
            help="Any FIFA/football CSV with player_name, overall, pace, etc.",
            key="csv_uploader",
        )
        if uploaded_file is not None:
            if st.session_state.dataset_source != uploaded_file.name:
                try:
                    raw_df = pd.read_csv(io.BytesIO(uploaded_file.read()))
                    tmp_path = Path("data/_uploaded.csv")
                    tmp_path.parent.mkdir(exist_ok=True)
                    raw_df.to_csv(tmp_path, index=False)
                    st.session_state.df = load_dataset(str(tmp_path))
                    st.session_state.dataset_source = uploaded_file.name
                    st.session_state.dataset_error = None
                    st.session_state.messages = []
                    st.rerun()
                except Exception as e:
                    st.session_state.dataset_error = str(e)
                    st.session_state.df = None
        else:
            # Uploader is empty — clear any previously loaded upload
            if st.session_state.dataset_source not in (None, "sample"):
                st.session_state.df = None
                st.session_state.dataset_source = None

    st.markdown('</div>', unsafe_allow_html=True)

    # Re-bind df after load
    df = st.session_state.df
    
    # -- Dataset status ------------------------------------------------------
    st.markdown(
        '<div class="sidebar-section"><h3>📊 Dataset Status</h3>',
        unsafe_allow_html=True
    )

    if df is not None:
        info = get_dataset_info(df)

        source_label = (
            "603-player sample"
            if st.session_state.dataset_source == "sample"
            else f"📎 {st.session_state.dataset_source}"
        )

        st.markdown(
            f'<div class="stat-grid">'
            f'<div class="stat-card"><div class="val">{info["total_players"]:,}</div><div class="lbl">Players</div></div>'
            f'<div class="stat-card"><div class="val">{info["total_clubs"]:,}</div><div class="lbl">Clubs</div></div>'
            f'<div class="stat-card"><div class="val">{info["total_nationalities"]}</div><div class="lbl">Nations</div></div>'
            f'<div class="stat-card"><div class="val">{info["avg_overall"]}</div><div class="lbl">Avg OVR</div></div>'
            f'</div>'
            f'<div style="margin-top:8px;" class="status-ok">\u2713 Loaded \u2014 {source_label}</div>',
            unsafe_allow_html=True,
        )


    elif st.session_state.dataset_error:
        st.markdown(
            f'<div class="status-err">✗ {st.session_state.dataset_error}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '''
            <div style="font-size:11px;color:#8899AA;margin-top:6px;">
                CSV must include:<br>
                <code>player_name, age, overall, position, club...</code>
            </div>
            ''',
            unsafe_allow_html=True
        )

    elif choice_key == "upload":
        st.markdown(
            '<div style="color:#8899AA;font-size:13px;">Upload a CSV above to get started.</div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            '<div style="color:#8899AA;font-size:13px;">Loading...</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


    # -- Player Reports (quick-launch) ---------------------------------------
    st.markdown(
        '<div class="sidebar-section"><h3>📋 Player Reports</h3>',
        unsafe_allow_html=True
    )
    if df is not None:
        player_names = sorted(df["player_name"].dropna().astype(str).unique())
        selected_player = st.selectbox(
            "Select Player",
            player_names,
            key="player_report_select",
            label_visibility="collapsed",
        )
        if st.button("📋 Generate Scouting Report", use_container_width=True, key="generate_report_btn"):
            st.session_state["prefill_query"] = f"Generate scouting report for {selected_player}"
            st.rerun()
    else:
        st.caption("Load a dataset to enable player reports.")
    st.markdown('</div>', unsafe_allow_html=True)

    # -- API status ----------------------------------------------------------
    st.markdown('<div class="sidebar-section"><h3>🤖 AI Status</h3>', unsafe_allow_html=True)
    if groq_client:
        st.markdown('<div class="status-ok">✓ Groq connected (LLaMA 3.3)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-err">✗ GROQ_API_KEY missing</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;color:#556677;margin-top:4px;">Set GROQ_API_KEY in .env or Streamlit secrets</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -- Example queries -----------------------------------------------------
    st.markdown('<div class="sidebar-section"><h3>💡 Example Queries</h3>', unsafe_allow_html=True)
    for q in EXAMPLE_QUERIES:
        if st.button(q, key=f"ex_{q}", use_container_width=True):
            st.session_state["prefill_query"] = q
    st.markdown('</div>', unsafe_allow_html=True)

    # -- Supported intents ---------------------------------------------------
    with st.expander("ℹ️ Supported Query Types"):
        st.markdown("""
        - **Top Players** — Best XI by rating/position
        - **Young Talent** — Rising stars by age
        - **Compare** — Head-to-head stats
        - **Filter** — Pace, shooting, nationality...
        - **Team Analysis** — Club averages
        - **Value / Gems** — Undervalued players
        - **Potential** — Future stars
        - **Player Report** — Full scouting report for any player
        """)

    # -- Clear chat ----------------------------------------------------------
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# -- Main area ---------------------------------------------------------------
st.markdown("""
<div class="scout-header">
    <span style="font-size:48px">⚽</span>
    <div>
        <h1>Maple <span class="badge">AI Scout</span><span class="badge-fifa">FIFA 2026</span></h1>
        <p>Your AI football scout — ask anything about players, clubs &amp; stats, powered by real FIFA data.</p>
    </div>
</div>
""", unsafe_allow_html=True)


# -- Dataset error guard -----------------------------------------------------
if st.session_state.dataset_error:
    st.markdown(f"""
    <div class="error-box">
        <strong>⚠️ Dataset Error</strong><br>{st.session_state.dataset_error}<br><br>
        📌 <b>Fix:</b> Upload a valid FIFA CSV using the <b>📂 Dataset</b> panel in the sidebar,
        or place your file at <code>data/fifa_players.csv</code> and restart.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# -- Render chat history -----------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="⚽"):
            _data = msg.get("data", {})

            if _data.get("error"):
                st.markdown(f'<div class="error-box">⚠️ {_data["error"]}</div>', unsafe_allow_html=True)
            else:
                if _data.get("title"):
                    st.markdown(f'<div class="result-title">{_data["title"]}</div>', unsafe_allow_html=True)

                if _data.get("table") is not None and not _data["table"].empty:
                    st.dataframe(_data["table"], use_container_width=True, hide_index=True)

                if _data.get("chart"):
                    st.plotly_chart(_data["chart"], use_container_width=True, config={"displayModeBar": False})

                if _data.get("chart2"):
                    st.plotly_chart(_data["chart2"], use_container_width=True, config={"displayModeBar": False})

                if _data.get("summary"):
                    st.markdown(f"""
                    <div class="insights-box">
                        <h4>🔍 Key Insights</h4>
                        <p>{_data['summary'].replace(chr(10), '<br>')}</p>
                    </div>
                    """, unsafe_allow_html=True)


# -- Chat input (handle prefill from sidebar buttons) ------------------------
prefill = st.session_state.pop("prefill_query", "")

if user_input := (st.chat_input("Ask Maple about players, clubs, stats...", key="main_input") or prefill):
    query = sanitize_query(user_input)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant", avatar="⚽"):
        _dataset_missing = df is None
        _api_missing = groq_client is None

        if _dataset_missing:
            st.markdown('<div class="error-box">⚠️ Dataset not loaded yet.</div>', unsafe_allow_html=True)
        elif _api_missing:
            st.markdown('<div class="error-box">⚠️ GROQ_API_KEY not configured. Please add it to your environment.</div>', unsafe_allow_html=True)

        if _dataset_missing or _api_missing:
            st.stop()

        with st.spinner("Maple is thinking..."):
            intent_obj = parse_query(query, groq_client)

        if intent_obj.get("intent") == "unsupported":
            err_msg = intent_obj.get("message", "Maple only supports FIFA dataset analytics queries.")
            st.markdown(f'<div class="error-box">⚠️ {err_msg}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant",
                "data": {"error": err_msg},
            })


        elif intent_obj.get("intent") == "player_report":
            # ── Player Performance Report — rich multi-section layout ───────
            with st.spinner("Generating scouting report..."):
                result_df, meta = route_intent(intent_obj, df)

            if meta.get("error"):
                st.markdown(f'<div class="error-box">⚠️ {meta["error"]}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "data": {"error": meta["error"]}})
            else:
                player_name = meta.get("player_name", "")
                st.markdown(f'<div class="result-title">📋 Scouting Report — {player_name}</div>', unsafe_allow_html=True)

                # -- Profile card ------------------------------------------
                st.markdown("**Player Profile**")
                st.dataframe(result_df, use_container_width=True, hide_index=True)

                # -- Radar + Percentile bars side-by-side ------------------
                col1, col2 = st.columns(2)
                with col1:
                    radar = chart_player_radar_single(meta.get("skill_snapshot", {}), player_name)
                    if radar:
                        st.plotly_chart(radar, use_container_width=True, config={"displayModeBar": False})
                with col2:
                    pct_chart = chart_percentile_bars(meta.get("percentiles", {}), player_name)
                    if pct_chart:
                        st.plotly_chart(pct_chart, use_container_width=True, config={"displayModeBar": False})

                # -- Strengths & Areas for Improvement ---------------------
                strengths   = meta.get("strengths", [])
                improvements = meta.get("improvements", [])
                col3, col4 = st.columns(2)
                with col3:
                    s_items = "".join(f"<li>✅ {s}</li>" for s in strengths) if strengths else "<li>No clear strengths identified</li>"
                    st.markdown(f"""
                    <div class="insights-box">
                        <h4>💪 Strengths</h4>
                        <ul style="margin:0;padding-left:18px;color:#B0C4D8;font-size:13px;line-height:1.8">{s_items}</ul>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    i_items = "".join(f"<li>📈 {i}</li>" for i in improvements) if improvements else "<li>No major weaknesses detected</li>"
                    st.markdown(f"""
                    <div class="insights-box">
                        <h4>🎯 Areas for Improvement</h4>
                        <ul style="margin:0;padding-left:18px;color:#B0C4D8;font-size:13px;line-height:1.8">{i_items}</ul>
                    </div>
                    """, unsafe_allow_html=True)

                # -- Similar Players ---------------------------------------
                similar = meta.get("similar_players", [])
                if similar:
                    pills = "".join(
                        f'<span style="background:rgba(0,212,164,0.12);border:1px solid rgba(0,212,164,0.3);'
                        f'border-radius:20px;padding:4px 12px;margin:3px;display:inline-block;'
                        f'font-size:12px;color:#00D4A4;">#{i+1} {p}</span>'
                        for i, p in enumerate(similar)
                    )
                    st.markdown(f"""
                    <div class="insights-box" style="margin-top:12px">
                        <h4>🤝 Similar Players (by stats)</h4>
                        <div style="margin-top:6px">{pills}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # -- AI Scout Summary -------------------------------------
                with st.spinner("Writing AI scout summary..."):
                    scout_summary = generate_scout_report(meta, groq_client)
                if scout_summary:
                    st.markdown(f"""
                    <div class="insights-box" style="margin-top:12px;border-color:rgba(0,133,255,0.3);background:linear-gradient(135deg,rgba(0,133,255,0.08),rgba(0,212,164,0.06))">
                        <h4>🧠 AI Scout Summary</h4>
                        <p>{scout_summary}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # -- PDF Export button --------------------------------------
                pdf_bytes = generate_pdf(
                    title=f"Scouting Report — {player_name}",
                    table_df=result_df,
                    summary=scout_summary or "",
                    strengths=strengths,
                    improvements=improvements,
                    similar=similar if similar else [],
                )
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{player_name.replace(' ', '_')}_scout_report.pdf",
                    mime="application/pdf",
                    key=f"pdf_{player_name}_{len(st.session_state.messages)}",
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "data": {
                        "title": f"Scouting Report — {player_name}",
                        "table": result_df,
                        "summary": scout_summary if scout_summary else "",
                    },
                })

        else:
            with st.spinner("Running analytics..."):
                result_df, meta = route_intent(intent_obj, df)

            response_data = {}

            if meta.get("error"):
                st.markdown(f'<div class="error-box">⚠️ {meta["error"]}</div>', unsafe_allow_html=True)
                response_data["error"] = meta["error"]

            else:
                title = meta.get("title", "Results")
                st.markdown(f'<div class="result-title">{title}</div>', unsafe_allow_html=True)
                response_data["title"] = title

                if not result_df.empty:
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                    response_data["table"] = result_df

                # -- Intent-specific charts ----------------------------------
                intent = meta.get("intent", "")
                chart = None
                chart2 = None

                if intent in ("top_players", "young_players", "filter_players", "potential_analysis"):
                    chart = chart_top_players(result_df, title)
                    chart2 = chart_age_vs_overall(df, result_df)

                elif intent == "team_analysis":
                    chart = chart_top_clubs(result_df, title)

                elif intent == "compare_players":
                    chart = chart_player_comparison(meta)

                elif intent == "value_analysis":
                    chart = chart_value_players(result_df)

                if chart:
                    st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
                    response_data["chart"] = chart

                if chart2:
                    st.plotly_chart(chart2, use_container_width=True, config={"displayModeBar": False})
                    response_data["chart2"] = chart2

                # -- AI summary ----------------------------------------------
                with st.spinner("Generating insights..."):
                    summary = generate_summary(result_df, meta, groq_client, query)

                if summary:
                    st.markdown(f"""
                    <div class="insights-box">
                        <h4>🔍 Key Insights</h4>
                        <p>{summary.replace(chr(10), '<br>')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    response_data["summary"] = summary

            # -- PDF Export button -----------------------------------------
            if not meta.get("error") and not result_df.empty:
                pdf_bytes = generate_pdf(
                    title=response_data.get("title", "Analytics Report"),
                    table_df=result_df,
                    summary=response_data.get("summary", ""),
                )
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name="maple_report.pdf",
                    mime="application/pdf",
                    key=f"pdf_analytics_{len(st.session_state.messages)}",
                )

            st.session_state.messages.append({
                "role": "assistant",
                "data": response_data,
            })
