import streamlit as st
import pandas as pd
from analyzer import analyze_data, get_data_profile
from llm_insights import get_insights, answer_question
from charts import generate_all_charts
from report import generate_pdf_report

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header { color: #666; font-size: 1rem; margin-bottom: 2rem; }
    .insight-box {
        background: #f8f9ff;
        border-left: 4px solid #667eea;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 AI Data Analyst</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload any CSV — AI analyzes, visualizes & explains in plain English</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    show_raw = st.checkbox("Show Raw Data", value=True)
    chart_theme = st.selectbox("Chart Theme", ["plotly", "plotly_dark", "ggplot2", "seaborn"])
    max_rows_preview = st.slider("Preview Rows", 5, 50, 10)
    st.divider()
    st.info("💡 Upload a CSV file to get started!")
    st.markdown("**Built with:**")
    st.markdown("🤖 Gemini AI | 🐼 Pandas | 📈 Plotly | 🎈 Streamlit")

uploaded_file = st.file_uploader(
    "📁 Upload your CSV file",
    type=["csv", "xlsx"],
    help="Upload a CSV or Excel file to analyze"
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {uploaded_file.name} — {df.shape[0]:,} rows × {df.shape[1]} columns")
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.stop()

    # Quick Stats
    st.subheader("⚡ Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Total Rows", f"{df.shape[0]:,}")
    col2.metric("📌 Columns", df.shape[1])
    col3.metric("❌ Missing Values", f"{df.isnull().sum().sum():,}")
    col4.metric("📊 Numeric Cols", len(df.select_dtypes(include='number').columns))

    # Raw Data Preview
    if show_raw:
        with st.expander("🔍 Raw Data Preview", expanded=True):
            st.dataframe(df.head(max_rows_preview), use_container_width=True)

    st.divider()

    # Data Profile
    st.subheader("🧬 Data Profile")
    profile = get_data_profile(df)
    with st.expander("📋 Column Details", expanded=False):
        st.dataframe(profile, use_container_width=True)

    st.divider()

    # AI Insights
    st.subheader("🤖 AI Insights")
    if "insights" not in st.session_state:
        st.session_state.insights = None

    if st.button("✨ Generate AI Insights", use_container_width=True):
        with st.spinner("🧠 AI is analyzing your data..."):
            insights = get_insights(df)
            st.session_state.insights = insights

    if st.session_state.insights:
        st.markdown(
            f'<div class="insight-box">{st.session_state.insights}</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # Charts
    st.subheader("📈 Auto-Generated Charts")
    generate_all_charts(df, chart_theme)

    st.divider()

    # Chat With Data
    st.subheader("💬 Chat With Your Data")
    st.caption("Ask any question about your dataset in plain English")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask anything... e.g. 'Which column has the most missing values?'")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = answer_question(df, question)
                st.write(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

    st.divider()

    # Download
    st.subheader("📥 Download Report")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf_report(
                    df, st.session_state.get("insights", "Run AI insights first.")
                )
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name="data_analysis_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    with col2:
        csv_data = df.describe().to_csv()
        st.download_button(
            label="⬇️ Download Stats CSV",
            data=csv_data,
            file_name="data_stats.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;background:#f8f9ff;
                border-radius:16px;border:2px dashed #667eea;">
        <div style="font-size:4rem;margin-bottom:1rem">📊</div>
        <h3 style="color:#667eea;">Upload a CSV to get started</h3>
        <p style="color:#888;">Works with sales, student, finance, sports, health data & more!</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🎯 What this tool does:")
    col1, col2, col3 = st.columns(3)
    col1.info("🔍 **Auto Profile**\nShows data types, missing values & statistics")
    col2.info("🤖 **AI Insights**\nGemini AI explains patterns in plain English")
    col3.info("📈 **Smart Charts**\nAuto-generates the best charts for your data")