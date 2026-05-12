import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import time
import urllib.parse

from toxic_words import calculate_toxicity_score, analyze_batch

st.set_page_config(
    page_title="🛡️ Kawach AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* ===== Global Dark Base ===== */
html, body, [class*="css"] {
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
}

/* ===== Hero Title ===== */
.hero-title {
    font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 900;
    background: linear-gradient(135deg, #FF4B4B 0%, #FF9B4B 50%, #FFD700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}

.hero-sub {
    text-align: center;
    color: #8B9099;
    font-size: clamp(0.85rem, 2.5vw, 1.05rem);
    margin-bottom: 2rem;
}

/* ===== Score Display ===== */
.score-box {
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
    border: 2px solid;
    transition: all 0.3s ease;
}

.score-safe {
    background: rgba(0, 200, 100, 0.1);
    border-color: #00C864;
    box-shadow: 0 0 30px rgba(0, 200, 100, 0.2);
}

.score-moderate {
    background: rgba(255, 180, 0, 0.1);
    border-color: #FFB400;
    box-shadow: 0 0 30px rgba(255, 180, 0, 0.2);
}

.score-toxic {
    background: rgba(255, 75, 75, 0.1);
    border-color: #FF4B4B;
    box-shadow: 0 0 30px rgba(255, 75, 75, 0.2);
    animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 30px rgba(255, 75, 75, 0.2); }
    50% { box-shadow: 0 0 50px rgba(255, 75, 75, 0.5); }
}

.score-number {
    font-size: clamp(3rem, 10vw, 5rem);
    font-weight: 900;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.score-number-safe  { color: #00C864; }
.score-number-moderate { color: #FFB400; }
.score-number-toxic { color: #FF4B4B; }

.score-label {
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ===== Trigger Words ===== */
.trigger-chip {
    display: inline-block;
    background: rgba(255, 75, 75, 0.15);
    border: 1px solid #FF4B4B;
    color: #FF7070;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 2px 3px;
    font-family: monospace;
}

/* ===== Info Cards ===== */
.info-card {
    background: #1E2130;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin: 0.6rem 0;
    border-left: 4px solid;
}

.card-explanation { border-left-color: #7B8CDE; }
.card-rewrite     { border-left-color: #00C864; }

.card-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #8B9099;
    margin-bottom: 0.4rem;
    font-weight: 700;
}

.card-body {
    font-size: 0.95rem;
    color: #DEDEDE;
    line-height: 1.6;
}

/* ===== Share Button ===== */
.share-btn {
    display: inline-block;
    background: #25D366;
    color: white !important;
    padding: 0.5rem 1.2rem;
    border-radius: 8px;
    font-weight: 700;
    text-decoration: none !important;
    font-size: 0.9rem;
    margin: 0.5rem 0;
    transition: opacity 0.2s;
}
.share-btn:hover { opacity: 0.85; }

/* ===== Section Dividers ===== */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #8B9099;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 1.5rem 0 0.7rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #2C3050;
}

/* ===== Footer ===== */
.footer {
    text-align: center;
    color: #555B70;
    font-size: 0.8rem;
    padding: 2rem 0 1rem;
    margin-top: 3rem;
    border-top: 1px solid #1E2130;
}
.footer a { color: #7B8CDE; text-decoration: none; }

/* ===== Stat Boxes ===== */
.stat-row {
    display: flex;
    gap: 1rem;
    margin: 0.5rem 0;
    flex-wrap: wrap;
}
.stat-box {
    flex: 1;
    min-width: 80px;
    background: #1E2130;
    border-radius: 10px;
    padding: 0.8rem;
    text-align: center;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 900;
}
.stat-label-text {
    font-size: 0.72rem;
    color: #8B9099;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ===== Mobile Responsive ===== */
@media (max-width: 640px) {
    .hero-title { font-size: 1.7rem; }
    .score-number { font-size: 3.5rem; }
    .stat-row { gap: 0.5rem; }
    .info-card { padding: 0.8rem 1rem; }
}

/* ===== Tabs Styling ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 0.4rem 1.2rem !important;
    background: #1E2130 !important;
    color: #8B9099 !important;
    border: 1px solid #2C3050 !important;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: rgba(255, 75, 75, 0.15) !important;
    color: #FF4B4B !important;
    border-color: #FF4B4B !important;
}

/* Hide Streamlit default elements */
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

def get_score_class(label: str) -> str:
    """CSS class based on label"""
    return {"Safe": "safe", "Moderate": "moderate", "Toxic": "toxic"}.get(label, "safe")


def render_score_box(result: dict):
    """Big score display box render karna"""
    score = result["score"]
    label = result["label"]
    css = get_score_class(label)

    emoji = {"Safe": "✅", "Moderate": "⚠️", "Toxic": "🚨"}.get(label, "")

    st.markdown(f"""
    <div class="score-box score-{css}">
        <div class="score-number score-number-{css}">{score}</div>
        <div class="score-label">{emoji} {label}</div>
        <div style="color:#8B9099; font-size:0.8rem; margin-top:0.3rem;">out of 100</div>
    </div>
    """, unsafe_allow_html=True)


def render_trigger_chips(triggers: list[str]):
    """Trigger words ko colored chips mein dikhana"""
    if not triggers:
        st.markdown('<p style="color:#00C864; font-size:0.9rem;">✅ No harmful words detected</p>',
                    unsafe_allow_html=True)
        return

    chips_html = " ".join(f'<span class="trigger-chip">{t}</span>' for t in triggers)
    st.markdown(chips_html, unsafe_allow_html=True)


def render_explanation(explanation: str):
    st.markdown(f"""
    <div class="info-card card-explanation">
        <div class="card-title">📋 Explanation</div>
        <div class="card-body">{explanation}</div>
    </div>
    """, unsafe_allow_html=True)


def render_rewrite(rewrite: str, original: str):
    if rewrite and rewrite != original:
        # Escape HTML characters in rewrite
        safe_rewrite = rewrite.replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(f"""
        <div class="info-card card-rewrite">
            <div class="card-title">✏️ Suggested Polite Rewrite</div>
            <div class="card-body" style="font-style:italic;">{safe_rewrite}</div>
        </div>
        """, unsafe_allow_html=True)


def whatsapp_share_button(text: str, score: int, label: str):
    """WhatsApp share button generate karna"""
    emoji = {"Safe": "✅", "Moderate": "⚠️", "Toxic": "🚨"}.get(label, "")
    msg = f"🛡️ Kawach AI Result\n\nText: \"{text[:80]}{'...' if len(text) > 80 else ''}\"\n\nScore: {score}/100\nVerdict: {emoji} {label}\n\nDetect toxicity at Kawach AI!"
    encoded = urllib.parse.quote(msg)
    url = f"https://wa.me/?text={encoded}"
    st.markdown(f'<a class="share-btn" href="{url}" target="_blank">📲 Share on WhatsApp</a>',
                unsafe_allow_html=True)


def build_results_dataframe(texts: list[str], results: list[dict]) -> pd.DataFrame:
    """Results ko DataFrame mein convert karna for download"""
    rows = []
    for text, r in zip(texts, results):
        rows.append({
            "comment": text,
            "score": r["score"],
            "label": r["label"],
            "triggers": ", ".join(r["triggers"]) if r["triggers"] else "",
            "rewrite": r.get("rewrite", ""),
        })
    return pd.DataFrame(rows)


def main():
    st.markdown('<h1 class="hero-title">🛡️ Kawach AI - Fight Online Abuse</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Detect Hindi · English · Hinglish toxicity in real-time. '
        'Keep online spaces safe for everyone.</p>',
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["💬 Single Text Analysis", "📂 CSV Batch Analysis"])

    with tab1:
        st.markdown('<div class="section-header">Enter Text to Analyze</div>', unsafe_allow_html=True)

        user_text = st.text_area(
            label="Type or paste any text (English, Hindi, Hinglish)",
            placeholder="e.g., 'Yaar tu bahut achha insaan hai!' or paste a social media comment...",
            height=130,
            label_visibility="collapsed",
            key="single_text_input",
        )

        col_btn, col_clear = st.columns([2, 1])
        with col_btn:
            analyze_btn = st.button("🔍 Analyze Now", use_container_width=True, type="primary")
        with col_clear:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)

        if clear_btn:
            st.session_state.pop("single_text_input", None)
            st.rerun()

        if user_text and len(user_text.strip()) > 3 and not analyze_btn:
            quick = calculate_toxicity_score(user_text)
            quick_css = get_score_class(quick["label"])
            quick_color = {"safe": "#00C864", "moderate": "#FFB400", "toxic": "#FF4B4B"}[quick_css]
            st.markdown(
                f'<p style="color:{quick_color}; font-size:0.82rem; margin-top:-0.5rem;">'
                f'🔄 Quick preview: {quick["label"]} ({quick["score"]}/100)</p>',
                unsafe_allow_html=True
            )

        if analyze_btn and user_text.strip():
            with st.spinner("🔍 Kawach AI analyzing..."):
                time.sleep(0.5)  # Small delay for UX
                result = calculate_toxicity_score(user_text)

            st.markdown('<div class="section-header">Analysis Results</div>', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1.5], gap="large")

            with col1:
                render_score_box(result)

                # Confetti / celebration for safe content
                if result["label"] == "Safe":
                    try:
                        from streamlit_extras.let_it_rain import rain
                        rain(emoji="🎉", font_size=28, falling_speed=4, animation_length=1)
                    except Exception:
                        st.success("🎉 Great! This text is safe and respectful.")

                # Progress bar as visual indicator
                score_color = {"Safe": "normal", "Moderate": "off", "Toxic": "normal"}.get(result["label"])
                st.markdown(f"**Toxicity Level**")
                st.progress(result["score"] / 100)

                # WhatsApp share
                st.markdown("---")
                whatsapp_share_button(user_text, result["score"], result["label"])

            with col2:
                # Trigger words
                st.markdown('<div class="section-header">⚡ Trigger Words Detected</div>', unsafe_allow_html=True)
                render_trigger_chips(result["triggers"])

                # Explanation
                render_explanation(result["explanation"])

                # Rewrite suggestion
                if result["triggers"]:
                    render_rewrite(result["rewrite"], user_text)

        elif analyze_btn and not user_text.strip():
            st.warning("⚠️ Please enter some text to analyze.")

        # ---- How it works expander ----
        with st.expander("ℹ️ How does Kawach AI score work?"):
            st.markdown("""
            | Score | Label | Meaning |
            |-------|-------|---------|
            | **0 – 24** | ✅ Safe | No harmful language detected |
            | **25 – 54** | ⚠️ Moderate | Some concerning words present |
            | **55 – 100** | 🚨 Toxic | Highly offensive content |

            **Scoring formula:**
            - Each toxic word has a severity weight (1×, 1.5×, or 3×)
            - Score = (weighted toxic words / total words) × 100
            - Positive words (not, sorry, please) reduce the score slightly
            - Score is capped at 100

            **Language support:** English · Hindi (romanized) · Hinglish · Mixed scripts
            """)

    with tab2:
        st.markdown('<div class="section-header">Upload CSV for Batch Analysis</div>', unsafe_allow_html=True)

        st.info("📋 Upload a CSV with a **`comment`** column. The app will score every row automatically.", icon="ℹ️")

        # Sample CSV download
        sample_data = pd.DataFrame({
            "comment": [
                "This is a great post, very informative!",
                "Tu bilkul bewakoof hai yaar",
                "Please be respectful to everyone.",
                "Ye content bahut bakwaas hai",
                "Amazing work, keep it up!",
            ]
        })
        sample_csv = sample_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Sample CSV",
            data=sample_csv,
            file_name="sample_comments.csv",
            mime="text/csv",
        )

        uploaded_file = st.file_uploader(
            "Drop your CSV here",
            type=["csv"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)

                if "comment" not in df.columns:
                    st.error('❌ CSV must have a **"comment"** column. Please check your file.')
                    st.write("Columns found:", list(df.columns))
                else:
                    total_rows = len(df)
                    st.success(f"✅ Loaded **{total_rows} rows** from `{uploaded_file.name}`")

                    if st.button("🚀 Run Batch Analysis", type="primary", use_container_width=True):
                        # Progress bar for batch processing
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        comments = df["comment"].tolist()
                        results = []

                        # Process in chunks for progress display
                        chunk_size = max(1, total_rows // 20)
                        for i in range(0, total_rows, chunk_size):
                            chunk = comments[i: i + chunk_size]
                            chunk_results = analyze_batch([str(c) for c in chunk])
                            results.extend(chunk_results)

                            progress = min((i + chunk_size) / total_rows, 1.0)
                            progress_bar.progress(progress)
                            status_text.text(f"Analyzing row {min(i + chunk_size, total_rows)} of {total_rows}...")
                            time.sleep(0.02)

                        progress_bar.empty()
                        status_text.empty()

                        # Build results dataframe
                        results_df = build_results_dataframe(comments, results)

                        # ---- SUMMARY STATS ----
                        st.markdown('<div class="section-header">📊 Summary Statistics</div>',
                                    unsafe_allow_html=True)

                        safe_count = (results_df["label"] == "Safe").sum()
                        moderate_count = (results_df["label"] == "Moderate").sum()
                        toxic_count = (results_df["label"] == "Toxic").sum()
                        avg_score = round(results_df["score"].mean(), 1)

                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric("✅ Safe", safe_count, f"{round(safe_count/total_rows*100)}%")
                        with c2:
                            st.metric("⚠️ Moderate", moderate_count, f"{round(moderate_count/total_rows*100)}%")
                        with c3:
                            st.metric("🚨 Toxic", toxic_count, f"{round(toxic_count/total_rows*100)}%")
                        with c4:
                            st.metric("📈 Avg Score", avg_score, "/ 100")

                        # ---- CHARTS ----
                        st.markdown('<div class="section-header">📈 Visual Breakdown</div>',
                                    unsafe_allow_html=True)

                        chart_col1, chart_col2 = st.columns(2)

                        with chart_col1:
                            # Pie chart - distribution
                            pie_data = pd.DataFrame({
                                "Label": ["Safe", "Moderate", "Toxic"],
                                "Count": [safe_count, moderate_count, toxic_count],
                            })
                            fig_pie = px.pie(
                                pie_data,
                                names="Label",
                                values="Count",
                                title="Content Distribution",
                                color="Label",
                                color_discrete_map={
                                    "Safe": "#00C864",
                                    "Moderate": "#FFB400",
                                    "Toxic": "#FF4B4B",
                                },
                                hole=0.45,
                            )
                            fig_pie.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                font_color="#FAFAFA",
                                title_font_size=14,
                                margin=dict(t=40, b=10, l=10, r=10),
                                legend=dict(font=dict(size=11)),
                            )
                            fig_pie.update_traces(textfont_size=13)
                            st.plotly_chart(fig_pie, use_container_width=True)

                        with chart_col2:
                            # Bar chart - score per row (first 50 for readability)
                            display_df = results_df.head(50).copy()
                            display_df["row"] = range(1, len(display_df) + 1)
                            color_map = {"Safe": "#00C864", "Moderate": "#FFB400", "Toxic": "#FF4B4B"}
                            display_df["color"] = display_df["label"].map(color_map)

                            fig_bar = px.bar(
                                display_df,
                                x="row",
                                y="score",
                                color="label",
                                title=f"Toxicity Score per Row (first {min(50, total_rows)})",
                                color_discrete_map=color_map,
                                labels={"row": "Row #", "score": "Toxicity Score"},
                            )
                            fig_bar.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                font_color="#FAFAFA",
                                title_font_size=14,
                                margin=dict(t=40, b=10, l=10, r=10),
                                xaxis=dict(gridcolor="#2C3050"),
                                yaxis=dict(gridcolor="#2C3050", range=[0, 105]),
                                legend=dict(font=dict(size=11)),
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)

                        # ---- TABLE PREVIEW (first 10 rows) ----
                        st.markdown('<div class="section-header">🗃️ Preview (First 10 Rows)</div>',
                                    unsafe_allow_html=True)

                        preview = results_df.head(10).copy()
                        preview["comment"] = preview["comment"].str[:80] + "..."

                        def color_label(val):
                            colors = {
                                "Safe": "color: #00C864; font-weight: bold",
                                "Moderate": "color: #FFB400; font-weight: bold",
                                "Toxic": "color: #FF4B4B; font-weight: bold",
                            }
                            return colors.get(val, "")

                        styled = preview[["comment", "score", "label", "triggers"]].style.applymap(
                            color_label, subset=["label"]
                        ).background_gradient(subset=["score"], cmap="RdYlGn_r", vmin=0, vmax=100)

                        st.dataframe(styled, use_container_width=True, height=320)

                        # ---- DOWNLOAD BUTTON ----
                        st.markdown('<div class="section-header">⬇️ Download Results</div>',
                                    unsafe_allow_html=True)

                        output_csv = results_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="📥 Download Full Results CSV",
                            data=output_csv,
                            file_name="kawach_ai_results.csv",
                            mime="text/csv",
                            use_container_width=True,
                            type="primary",
                        )

                        st.caption(f"Results include {total_rows} rows with score, label, triggers, and rewrite columns.")

            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Make sure your CSV is properly formatted and has a 'comment' column.")

    # ==========================================================================
    # FOOTER
    # ==========================================================================
    st.markdown("""
    <div class="footer">
        🛡️ <strong>Kawach AI</strong> — Open Source Toxicity Detector for Hindi · English · Hinglish<br>
        Built with ❤️ | <a href="https://github.com" target="_blank">GitHub</a> |
        Fighting online hate, one comment at a time.<br>
        <span style="color:#3C4060;">v1.0 · Rule-based NLP · No data stored</span>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
