import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None


def _build_context(df: pd.DataFrame) -> str:
    """Build a concise dataset context string for the LLM."""
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    context = f"""
Dataset Overview:
- Shape: {df.shape[0]} rows x {df.shape[1]} columns
- Columns: {list(df.columns)}
- Numeric columns: {numeric_cols}
- Categorical columns: {categorical_cols}
- Missing values: {df.isnull().sum().sum()}
- Duplicate rows: {df.duplicated().sum()}

Sample Data (first 5 rows):
{df.head(5).to_string()}

Statistical Summary:
{df.describe().round(2).to_string() if numeric_cols else 'No numeric columns'}
"""
    return context


def get_insights(df: pd.DataFrame) -> str:
    """Generate AI insights about the entire dataset."""
    if model is None:
        return (
            "⚠️ GEMINI_API_KEY not found. "
            "Please add your API key to the .env file."
        )

    context = _build_context(df)
    prompt = f"""
You are an expert data analyst. Analyze the following dataset.

{context}

Provide:
1. **What is this dataset about?** (2-3 sentences)
2. **Key Patterns & Trends** (3-4 bullet points)
3. **Important Statistics** (highlight the most interesting numbers)
4. **Data Quality Issues** (missing values, outliers, duplicates)
5. **Business Recommendations** (2-3 actionable insights)

Write in simple plain English. Use bullet points. Format with markdown.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating insights: {str(e)}"


def answer_question(df: pd.DataFrame, question: str) -> str:
    """Answer a specific question about the dataset."""
    if model is None:
        return "⚠️ GEMINI_API_KEY not found. Please add your key to .env file."

    context = _build_context(df)
    prompt = f"""
You are an expert data analyst. Answer this question about the dataset.

{context}

Question: {question}

Instructions:
- Give a direct, clear answer in plain English
- Include specific numbers from the data when relevant
- If the question cannot be answered from the data, say so clearly
- Keep the answer concise (2-5 sentences max)
- Format with markdown if helpful
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"