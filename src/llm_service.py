"""
llm_service.py
Groq client initialisation + AI summary generation for analytics results.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import pandas as pd
import streamlit as st

# Load .env early so os.getenv() works before Streamlit secrets are checked
load_dotenv()


def get_groq_client() -> Groq | None:
    """Initialise and return a Groq client using the API key from env or Streamlit secrets."""
    # 1. Try environment variable first (populated from .env via load_dotenv above)
    api_key = os.getenv("GROQ_API_KEY")

    # 2. Fall back to Streamlit secrets only if env var is absent.
    #    Wrap in try/except because st.secrets raises StreamlitSecretNotFoundError
    #    when no secrets.toml file exists at all (not just a missing key).
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY", None)
        except Exception:
            api_key = None

    if not api_key:
        return None
    return Groq(api_key=api_key)


def generate_summary(
    result_df: pd.DataFrame,
    meta: dict,
    groq_client: Groq,
    query: str = "",
) -> str:
    """
    Generate a concise 3-bullet-point AI summary of the analytics result.
    Falls back to a placeholder if the client is unavailable.
    """
    if groq_client is None:
        return "_AI summaries unavailable — GROQ_API_KEY not set._"

    if result_df.empty:
        return ""

    # Prepare a compact text snapshot (max 30 rows to stay within token budget)
    sample = result_df.head(30).to_string(index=False)
    title = meta.get("title", "FIFA Analysis Results")

    prompt = f"""You are a football analytics expert. Below are structured FIFA data results.
Query: "{query}"
Analysis type: {title}

Data:
{sample}

Summarize the key findings in EXACTLY 3 concise bullet points.
Rules:
- Maximum 80 words total
- Use only information from the data provided — no hallucinations
- Be specific: mention player names, numbers, clubs where relevant
- Start each bullet with •
- No headers, no extra text
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"_Summary generation failed: {e}_"
