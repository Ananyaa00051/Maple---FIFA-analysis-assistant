"""
intent_router.py
Routes a parsed intent dict to the correct analytics function.
"""

import pandas as pd
from src.analytics import (
    get_top_players,
    get_young_players,
    compare_players,
    filter_players,
    analyze_teams,
    get_value_players,
    get_potential_players,
    get_player_report,
)


def route_intent(intent_obj: dict, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Dispatch parsed intent to the appropriate analytics function.
    Returns (result_df, meta_dict).
    meta_dict may contain: title, error, intent, count, etc.
    """
    intent = intent_obj.get("intent", "unsupported")
    meta_base = {"intent": intent}

    # ── Unsupported ────────────────────────────────────────────────────────
    if intent == "unsupported":
        msg = intent_obj.get("message", "This assistant only supports FIFA dataset analytics queries.")
        return pd.DataFrame(), {**meta_base, "error": msg}

    # ── Top Players ────────────────────────────────────────────────────────
    if intent == "top_players":
        filters = intent_obj.get("filters", {}) or {}
        result, meta = get_top_players(
            df,
            position=filters.get("position"),
            limit=int(intent_obj.get("limit", 10)),
            sort_by=intent_obj.get("sort_by", "overall"),
        )
        return result, {**meta_base, **meta}

    # ── Young Players ──────────────────────────────────────────────────────
    if intent == "young_players":
        filters = intent_obj.get("filters", {}) or {}
        result, meta = get_young_players(
            df,
            age_max=int(filters.get("age_max", 23)),
            position=filters.get("position"),
            limit=int(intent_obj.get("limit", 10)),
            sort_by=intent_obj.get("sort_by", "potential"),
        )
        return result, {**meta_base, **meta}

    # ── Compare Players ────────────────────────────────────────────────────
    if intent == "compare_players":
        players = intent_obj.get("players", [])
        result, meta = compare_players(df, players)
        return result, {**meta_base, **meta}

    # ── Filter Players ─────────────────────────────────────────────────────
    if intent == "filter_players":
        filters = intent_obj.get("filters", {}) or {}
        result, meta = filter_players(
            df,
            filters=filters,
            limit=int(intent_obj.get("limit", 10)),
            sort_by=intent_obj.get("sort_by", "overall"),
        )
        return result, {**meta_base, **meta}

    # ── Team Analysis ──────────────────────────────────────────────────────
    if intent == "team_analysis":
        result, meta = analyze_teams(
            df,
            metric=intent_obj.get("metric", "overall"),
            limit=int(intent_obj.get("limit", 10)),
        )
        return result, {**meta_base, **meta}

    # ── Value Analysis ─────────────────────────────────────────────────────
    if intent == "value_analysis":
        filters = intent_obj.get("filters", {}) or {}
        result, meta = get_value_players(
            df,
            filters=filters,
            limit=int(intent_obj.get("limit", 10)),
        )
        return result, {**meta_base, **meta}

    # ── Potential Analysis ─────────────────────────────────────────────────
    if intent == "potential_analysis":
        filters = intent_obj.get("filters", {}) or {}
        result, meta = get_potential_players(
            df,
            potential_min=int(filters.get("potential_min", 85)),
            age_max=filters.get("age_max"),
            position=filters.get("position"),
            limit=int(intent_obj.get("limit", 10)),
        )
        return result, {**meta_base, **meta}

    # ── Player Report ──────────────────────────────────────────────────────
    if intent == "player_report":
        player_name = intent_obj.get("player_name", "")
        result, meta = get_player_report(df, player_name)
        return result, {**meta_base, **meta}

    # ── Fallback ───────────────────────────────────────────────────────────
    return pd.DataFrame(), {**meta_base, "error": f"Unhandled intent: '{intent}'."}
