import os
import tempfile
import csv
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools

load_dotenv()

st.set_page_config(
    page_title="BizAnalyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

EXAMPLE_QUESTIONS = [
    "What was my best revenue month?",
    "Which product sold the most?",
    "Show me month on month growth",
    "Which city had the highest sales?",
]


def preprocess_and_save(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None

        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).replace({r'"': '""'}, regex=True)

        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_path = temp_file.name
            df.to_csv(temp_path, index=False, quoting=csv.QUOTE_ALL)

        return temp_path, df.columns.tolist(), df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None, None


def set_query(q: str):
    st.session_state.user_query = q


st.markdown(
    """
    <style>
        .block-container { padding-top: 2.5rem; max-width: 1100px; }
        .biz-title { font-size: 2.4rem; font-weight: 700; margin-bottom: 0.2rem; }
        .biz-subtitle { color: #6b7280; font-size: 1.05rem; margin-bottom: 1.5rem; }
        .section-label { font-weight: 600; color: #374151; margin-top: 0.5rem; margin-bottom: 0.5rem; }
        div.stButton > button {
            width: 100%;
            text-align: left;
            white-space: normal;
            padding: 0.7rem 0.9rem;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            background-color: #ffffff;
            color: #111827;
            font-weight: 500;
            transition: all 0.15s ease-in-out;
        }
        div.stButton > button:hover {
            border-color: #6366f1;
            background-color: #f5f7ff;
            color: #4f46e5;
        }
        div[data-testid="stForm"] button[kind="primaryFormSubmit"],
        button[kind="primary"] {
            background-color: #4f46e5 !important;
            color: #ffffff !important;
            border: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="biz-title">BizAnalyst 📊</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="biz-subtitle">Your AI data analyst — made for Bengaluru startups</div>',
    unsafe_allow_html=True,
)

anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_key:
    st.error("ANTHROPIC_API_KEY not found. Please add it to the .env file.")
    st.stop()

st.markdown('<div class="section-label">1. Upload your data</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "CSV or Excel file",
    type=["csv", "xlsx"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    temp_path, columns, df = preprocess_and_save(uploaded_file)

    if temp_path and columns and df is not None:
        with st.expander(f"Preview data — {len(df):,} rows × {len(columns)} columns", expanded=False):
            st.dataframe(df, use_container_width=True)
            st.caption("Columns: " + ", ".join(columns))

        duckdb_tools = DuckDbTools()
        duckdb_tools.load_local_csv_to_table(path=temp_path, table="uploaded_data")

        data_analyst_agent = Agent(
            model=Claude(id="claude-sonnet-4-5", api_key=anthropic_key),
            tools=[duckdb_tools, PandasTools()],
            system_message=(
                "You are an expert data analyst helping a startup founder in Bengaluru. "
                "Use the 'uploaded_data' table to answer user queries. Generate SQL queries "
                "using DuckDB tools to solve the user's query. Provide clear, concise answers "
                "with the results and a brief business interpretation."
            ),
            markdown=True,
        )

        st.markdown('<div class="section-label">2. Try an example</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, q in enumerate(EXAMPLE_QUESTIONS):
            with cols[i % 2]:
                st.button(q, key=f"ex_{i}", on_click=set_query, args=(q,))

        st.markdown('<div class="section-label">3. Or ask your own question</div>', unsafe_allow_html=True)
        user_query = st.text_area(
            "Your question",
            key="user_query",
            placeholder="e.g. What were my top 5 customers by revenue last quarter?",
            label_visibility="collapsed",
            height=100,
        )

        submit = st.button("Run analysis", type="primary")

        if submit:
            if not user_query.strip():
                st.warning("Please enter a question or pick an example above.")
            else:
                try:
                    with st.spinner("Analysing your data..."):
                        response = data_analyst_agent.run(user_query)
                        response_content = response.content if hasattr(response, "content") else str(response)
                    st.markdown("#### Answer")
                    st.markdown(response_content)
                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")
else:
    st.info("Upload a CSV or Excel file to get started.")
