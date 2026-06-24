"""
query_parser.py
Uses Groq LLM to classify user queries into structured intents + parameters.
Groq does NOT answer football questions directly — it only classifies intent.
"""

import json
import re
from groq import Groq
import streamlit as st


SUPPORTED_INTENTS = [
    "top_players",
    "young_players",
    "compare_players",
    "filter_players",
    "team_analysis",
    "value_analysis",
    "potential_analysis",
    "player_report",
    "unsupported",
]

SYSTEM_PROMPT = """You are a query parser for a FIFA football analytics application.
Your ONLY job is to convert user questions into a structured JSON intent object.
Do NOT answer the question. Do NOT provide football knowledge. ONLY output valid JSON.

Supported intents and their parameters:

1. top_players - Ranking players by overall rating
   {"intent": "top_players", "filters": {"position": "ST|CM|CB|GK|etc or null"}, "limit": 10, "sort_by": "overall"}

2. young_players - Young talent discovery
   {"intent": "young_players", "filters": {"age_max": 23, "position": null}, "limit": 10, "sort_by": "potential"}

3. compare_players - Compare two specific players
   {"intent": "compare_players", "players": ["Player Name 1", "Player Name 2"]}

4. filter_players - Filter by attributes
   {"intent": "filter_players", "filters": {"position": null, "nationality": null, "club": null, "age_max": null, "age_min": null, "overall_min": null, "pace_min": null, "shooting_min": null, "passing_min": null, "dribbling_min": null, "defending_min": null}, "limit": 10, "sort_by": "overall"}

5. team_analysis - Analyze clubs/teams
   {"intent": "team_analysis", "metric": "overall|potential", "limit": 10}

6. value_analysis - Best value / hidden gems
   {"intent": "value_analysis", "filters": {"position": null, "age_max": null}, "limit": 10}

7. potential_analysis - High potential players
   {"intent": "potential_analysis", "filters": {"potential_min": 85, "age_max": null, "position": null}, "limit": 10}

8. player_report - Full scouting report for a single named player
   {"intent": "player_report", "player_name": "Exact Player Name"}
   Trigger phrases: "report on", "analyze", "analyse", "scout", "profile", "tell me about", "scouting report", "performance report"

9. unsupported - Query not related to FIFA data analytics
   {"intent": "unsupported", "message": "brief reason"}

Rules:
- Output ONLY valid JSON. No markdown, no explanation, no extra text.
- Extract player names exactly as mentioned for compare_players.
- For position filters use common abbreviations: ST, CF, LW, RW, CAM, CM, CDM, LB, RB, CB, GK, LM, RM, LAM, RAM, LS, RS, SS, LF, RF
- If user asks about "strikers" use position="ST", "defenders"="CB", "midfielders"="CM", "goalkeepers"="GK", "wingers" check LW or RW.
- Default limit is 10 unless user specifies otherwise.
- For value/hidden gems queries use value_analysis intent.
- If the query is about Champions League predictions, real-world events, or non-FIFA-data topics, use unsupported.
"""


def parse_query(user_query: str, groq_client: Groq) -> dict:
    """
    Send the user query to Groq for intent classification.
    Returns a structured dict with intent and parameters.
    """
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
            temperature=0.1,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

        parsed = json.loads(raw)

        if "intent" not in parsed or parsed["intent"] not in SUPPORTED_INTENTS:
            return {"intent": "unsupported", "message": "Could not classify query."}

        return parsed

    except json.JSONDecodeError:
        return {"intent": "unsupported", "message": "Failed to parse LLM response as JSON."}
    except Exception as e:
        return {"intent": "unsupported", "message": f"Query parsing error: {str(e)}"}
