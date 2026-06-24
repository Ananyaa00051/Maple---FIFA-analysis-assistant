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


def generate_scout_report(meta: dict, groq_client: Groq) -> str:
    """
    Generate a professional AI scout summary for a Player Performance Report.
    Uses percentiles, strengths, and profile data to write a grounded paragraph.
    """
    if groq_client is None:
        return "_AI scout summary unavailable — GROQ_API_KEY not set._"

    profile     = meta.get("profile", {})
    percentiles = meta.get("percentiles", {})
    strengths   = meta.get("strengths", [])
    improvements = meta.get("improvements", [])
    similar     = meta.get("similar_players", [])
    name        = meta.get("player_name", "This player")

    pct_lines = "\n".join(
        f"  - {k.capitalize()}: {v}th percentile (Top {round(100-v,1)}%)"
        for k, v in percentiles.items()
    )
    strengths_text   = "\n".join(f"  • {s}" for s in strengths)   or "  • None identified"
    improve_text     = "\n".join(f"  • {s}" for s in improvements) or "  • None identified"
    similar_text     = ", ".join(similar) if similar else "N/A"

    prompt = f"""You are a professional football scout writing a report for a scouting database.
Write a concise, professional scout summary for {name} using ONLY the data below.

Player Profile:
  Name: {profile.get('Name')}, Age: {profile.get('Age')}, Club: {profile.get('Club')}
  Position: {profile.get('Position')}, Overall: {profile.get('Overall')}, Potential: {profile.get('Potential')}
  Market Value: {profile.get('Value')}

League Percentile Rankings (vs all players in dataset):
{pct_lines}

Strengths:
{strengths_text}

Areas for Improvement:
{improve_text}

Similar Players (by stats): {similar_text}

Write a professional scout summary of EXACTLY 3-4 sentences.
Rules:
- Use only the data provided — no hallucinations or real-world knowledge
- Mention specific percentiles or stats to justify claims
- Be analytical, not generic ("elite" is fine only if percentile supports it)
- End with one forward-looking sentence about potential or role suitability
- No bullet points, no headers — flowing paragraph only
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"_Scout summary generation failed: {e}_"
