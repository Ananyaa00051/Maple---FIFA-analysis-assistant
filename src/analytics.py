"""
analytics.py
Core analytics engine — all Pandas operations live here.
Each function returns a (DataFrame, metadata_dict) tuple.
"""

import pandas as pd
import numpy as np
from typing import Optional


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _safe_str(val) -> str:
    return str(val).strip() if val is not None else ""


def _format_value(v: float) -> str:
    """Format EUR values for display."""
    if v >= 1_000_000:
        return f"€{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"€{v/1_000:.0f}K"
    return f"€{v:.0f}"


def _find_player(df: pd.DataFrame, name: str) -> pd.Series | None:
    """Case-insensitive player search, returns best match or None."""
    name_lower = name.lower().strip()
    mask = df["player_name"].str.lower().str.contains(name_lower, na=False)
    matches = df[mask]
    if matches.empty:
        return None
    # Return highest overall rated match if multiple
    return matches.sort_values("overall", ascending=False).iloc[0]


# ---------------------------------------------------------------------------
# Feature 1: Top Players Ranking
# ---------------------------------------------------------------------------

def get_top_players(
    df: pd.DataFrame,
    position: Optional[str] = None,
    limit: int = 10,
    sort_by: str = "overall",
) -> tuple[pd.DataFrame, dict]:
    """Rank players by overall (or another stat), optionally by position."""
    data = df.copy()

    if position:
        data = data[data["position"].str.upper() == position.upper()]

    if data.empty:
        return pd.DataFrame(), {"error": f"No players found for position '{position}'."}

    valid_sort = sort_by if sort_by in data.columns else "overall"
    data = data.sort_values(valid_sort, ascending=False).head(limit)

    result = data[["player_name", "club", "nationality", "position", "overall", "potential", "age"]].copy()
    result.insert(0, "rank", range(1, len(result) + 1))
    result.columns = ["#", "Player", "Club", "Nationality", "Position", "Overall", "Potential", "Age"]

    meta = {
        "title": f"Top {limit} Players" + (f" — {position}" if position else ""),
        "sort_by": valid_sort,
        "count": len(result),
    }
    return result, meta


# ---------------------------------------------------------------------------
# Feature 2: Young Talent Discovery
# ---------------------------------------------------------------------------

def get_young_players(
    df: pd.DataFrame,
    age_max: int = 23,
    position: Optional[str] = None,
    limit: int = 10,
    sort_by: str = "potential",
) -> tuple[pd.DataFrame, dict]:
    """Find the best young players under a given age."""
    data = df[df["age"] <= age_max].copy()

    if position:
        data = data[data["position"].str.upper() == position.upper()]

    if data.empty:
        return pd.DataFrame(), {"error": f"No players under age {age_max}" + (f" at {position}" if position else "") + "."}

    valid_sort = sort_by if sort_by in data.columns else "potential"
    data = data.sort_values(valid_sort, ascending=False).head(limit)

    result = data[["player_name", "club", "nationality", "position", "age", "overall", "potential"]].copy()
    result.insert(0, "rank", range(1, len(result) + 1))
    result.columns = ["#", "Player", "Club", "Nationality", "Position", "Age", "Overall", "Potential"]

    meta = {
        "title": f"Best Young Players (Under {age_max})" + (f" — {position}" if position else ""),
        "sort_by": valid_sort,
        "count": len(result),
    }
    return result, meta


# ---------------------------------------------------------------------------
# Feature 3: Player Comparison
# ---------------------------------------------------------------------------

COMPARISON_METRICS = ["overall", "potential", "pace", "shooting", "passing", "dribbling", "defending", "physicality"]


def compare_players(df: pd.DataFrame, player_names: list[str]) -> tuple[pd.DataFrame, dict]:
    """Compare two players across key metrics."""
    if len(player_names) < 2:
        return pd.DataFrame(), {"error": "Please provide exactly two player names to compare."}

    p1_row = _find_player(df, player_names[0])
    p2_row = _find_player(df, player_names[1])

    errors = []
    if p1_row is None:
        errors.append(f"Player '{player_names[0]}' not found in dataset.")
    if p2_row is None:
        errors.append(f"Player '{player_names[1]}' not found in dataset.")

    if errors:
        return pd.DataFrame(), {"error": " | ".join(errors)}

    p1_name = p1_row["player_name"]
    p2_name = p2_row["player_name"]

    rows = []
    for metric in COMPARISON_METRICS:
        v1 = int(p1_row[metric]) if metric in p1_row else 0
        v2 = int(p2_row[metric]) if metric in p2_row else 0
        winner = p1_name if v1 > v2 else (p2_name if v2 > v1 else "Draw")
        rows.append({
            "Metric": metric.capitalize(),
            p1_name: v1,
            p2_name: v2,
            "Edge": winner,
        })

    result = pd.DataFrame(rows)

    # Player info for subtitle
    info = {
        p1_name: f"{p1_row['position']} · {p1_row['club']} · Age {p1_row['age']}",
        p2_name: f"{p2_row['position']} · {p2_row['club']} · Age {p2_row['age']}",
    }

    meta = {
        "title": f"{p1_name}  vs  {p2_name}",
        "players": [p1_name, p2_name],
        "info": info,
        "p1": p1_row,
        "p2": p2_row,
    }
    return result, meta


# ---------------------------------------------------------------------------
# Feature 4: Advanced Filtering
# ---------------------------------------------------------------------------

def filter_players(
    df: pd.DataFrame,
    filters: dict,
    limit: int = 10,
    sort_by: str = "overall",
) -> tuple[pd.DataFrame, dict]:
    """Filter players by arbitrary attribute combinations."""
    data = df.copy()
    applied = []

    str_filters = {
        "position": ("position", lambda df, v: df["position"].str.upper() == v.upper()),
        "nationality": ("nationality", lambda df, v: df["nationality"].str.lower() == v.lower()),
        "club": ("club", lambda df, v: df["club"].str.lower().str.contains(v.lower(), na=False)),
    }

    num_filters = {
        "age_max": ("age", "<="),
        "age_min": ("age", ">="),
        "overall_min": ("overall", ">="),
        "potential_min": ("potential", ">="),
        "pace_min": ("pace", ">="),
        "shooting_min": ("shooting", ">="),
        "passing_min": ("passing", ">="),
        "dribbling_min": ("dribbling", ">="),
        "defending_min": ("defending", ">="),
    }

    for key, (col, fn) in str_filters.items():
        val = filters.get(key)
        if val:
            data = data[fn(data, val)]
            applied.append(f"{key}={val}")

    for key, (col, op) in num_filters.items():
        val = filters.get(key)
        if val is not None:
            try:
                v = float(val)
                if op == "<=":
                    data = data[data[col] <= v]
                elif op == ">=":
                    data = data[data[col] >= v]
                applied.append(f"{col}{op}{val}")
            except (ValueError, TypeError):
                pass

    if data.empty:
        return pd.DataFrame(), {"error": "No matching players found for the given filters."}

    valid_sort = sort_by if sort_by in data.columns else "overall"
    data = data.sort_values(valid_sort, ascending=False).head(limit)

    display_cols = ["player_name", "club", "nationality", "position", "age", "overall", "potential",
                    "pace", "shooting", "passing", "dribbling", "defending", "physicality"]
    display_cols = [c for c in display_cols if c in data.columns]
    result = data[display_cols].copy()
    result.insert(0, "rank", range(1, len(result) + 1))
    friendly = {
        "player_name": "Player", "club": "Club", "nationality": "Nationality",
        "position": "Position", "age": "Age", "overall": "Overall",
        "potential": "Potential", "pace": "Pace", "shooting": "Shooting",
        "passing": "Passing", "dribbling": "Dribbling", "defending": "Defending",
        "physicality": "Physicality",
    }
    result.columns = ["#"] + [friendly.get(c, c.capitalize()) for c in display_cols]

    meta = {
        "title": f"Filtered Players ({', '.join(applied) if applied else 'all'})",
        "filters_applied": applied,
        "count": len(result),
    }
    return result, meta


# ---------------------------------------------------------------------------
# Feature 5: Team / Club Analysis
# ---------------------------------------------------------------------------

def analyze_teams(
    df: pd.DataFrame,
    metric: str = "overall",
    limit: int = 10,
) -> tuple[pd.DataFrame, dict]:
    """Aggregate player stats by club."""
    valid_metric = metric if metric in df.columns else "overall"

    team_stats = (
        df.groupby("club")
        .agg(
            avg_overall=("overall", "mean"),
            avg_potential=("potential", "mean"),
            avg_age=("age", "mean"),
            player_count=("player_name", "count"),
        )
        .reset_index()
    )

    sort_col = f"avg_{valid_metric}" if f"avg_{valid_metric}" in team_stats.columns else "avg_overall"
    team_stats = team_stats.sort_values(sort_col, ascending=False).head(limit)

    team_stats["avg_overall"] = team_stats["avg_overall"].round(1)
    team_stats["avg_potential"] = team_stats["avg_potential"].round(1)
    team_stats["avg_age"] = team_stats["avg_age"].round(1)

    team_stats.insert(0, "rank", range(1, len(team_stats) + 1))
    team_stats.columns = ["#", "Club", "Avg Overall", "Avg Potential", "Avg Age", "Squad Size"]

    meta = {
        "title": f"Top {limit} Clubs by Avg {valid_metric.capitalize()}",
        "metric": valid_metric,
        "count": len(team_stats),
    }
    return team_stats, meta


# ---------------------------------------------------------------------------
# Feature 6: Hidden Gems / Best Value Players
# ---------------------------------------------------------------------------

def get_value_players(
    df: pd.DataFrame,
    filters: dict = None,
    limit: int = 10,
) -> tuple[pd.DataFrame, dict]:
    """Find undervalued players using value_score = (overall + potential) / value_eur."""
    data = df[df["value_eur"] > 0].copy()

    if filters:
        pos = filters.get("position")
        age_max = filters.get("age_max")
        if pos:
            data = data[data["position"].str.upper() == pos.upper()]
        if age_max:
            try:
                data = data[data["age"] <= int(age_max)]
            except (ValueError, TypeError):
                pass

    if data.empty:
        return pd.DataFrame(), {"error": "No players with valid market values found."}

    data["value_score"] = ((data["overall"] + data["potential"]) / data["value_eur"] * 1_000_000).round(3)
    data = data.sort_values("value_score", ascending=False).head(limit)

    result = data[["player_name", "club", "position", "age", "overall", "potential", "value_eur", "value_score"]].copy()
    result["value_eur"] = result["value_eur"].apply(_format_value)
    result.insert(0, "rank", range(1, len(result) + 1))
    result.columns = ["#", "Player", "Club", "Position", "Age", "Overall", "Potential", "Market Value", "Value Score"]

    meta = {
        "title": "Best Value Players (Hidden Gems)",
        "count": len(result),
    }
    return result, meta


# ---------------------------------------------------------------------------
# Feature 7: High Potential Players
# ---------------------------------------------------------------------------

def get_potential_players(
    df: pd.DataFrame,
    potential_min: int = 85,
    age_max: Optional[int] = None,
    position: Optional[str] = None,
    limit: int = 10,
) -> tuple[pd.DataFrame, dict]:
    """Find players with high potential."""
    data = df[df["potential"] >= potential_min].copy()

    if age_max:
        data = data[data["age"] <= age_max]
    if position:
        data = data[data["position"].str.upper() == position.upper()]

    if data.empty:
        return pd.DataFrame(), {"error": f"No players found with potential ≥ {potential_min}."}

    data = data.sort_values("potential", ascending=False).head(limit)
    result = data[["player_name", "club", "nationality", "position", "age", "overall", "potential"]].copy()
    result.insert(0, "rank", range(1, len(result) + 1))
    result.columns = ["#", "Player", "Club", "Nationality", "Position", "Age", "Overall", "Potential"]

    meta = {
        "title": f"High Potential Players (Potential ≥ {potential_min})" + (f", Under {age_max}" if age_max else ""),
        "potential_min": potential_min,
        "count": len(result),
    }
    return result, meta


# ---------------------------------------------------------------------------
# Feature 8: Player Performance Report
# ---------------------------------------------------------------------------

SKILL_COLS = ["pace", "shooting", "passing", "dribbling", "defending", "physicality"]

_STRENGTH_LABELS = {
    "pace":         "Elite pace and acceleration",
    "shooting":     "Clinical finishing and shooting",
    "passing":      "Exceptional vision and passing range",
    "dribbling":    "Outstanding dribbling and ball control",
    "defending":    "Strong defensive output and positioning",
    "physicality":  "Dominant physical presence",
}

_IMPROVE_LABELS = {
    "pace":         "Pace and acceleration",
    "shooting":     "Finishing and shooting efficiency",
    "passing":      "Distribution and passing range",
    "dribbling":    "Ball control and dribbling",
    "defending":    "Defensive contribution",
    "physicality":  "Physical strength and aerial presence",
}


def get_player_report(
    df: pd.DataFrame,
    player_name: str,
) -> tuple[pd.DataFrame, dict]:
    """
    Generate a comprehensive scouting report for a single player.
    Returns a profile DataFrame and a rich meta dict containing:
      - percentiles across 6 skill attributes vs. the full dataset
      - strengths (top-25th-percentile attributes)
      - areas for improvement (bottom-50th-percentile attributes)
      - 5 most similar players found via KNN on skill stats
    """
    player = _find_player(df, player_name)
    if player is None:
        return pd.DataFrame(), {"error": f"Player '{player_name}' not found in dataset."}

    # -- Percentiles (vs. whole dataset) ------------------------------------
    available_skills = [c for c in SKILL_COLS if c in df.columns]
    percentiles: dict[str, float] = {}
    for col in available_skills:
        pct = float((df[col] < player[col]).mean() * 100)
        percentiles[col] = round(pct, 1)

    # -- Strengths & areas for improvement ----------------------------------
    strengths = [_STRENGTH_LABELS[c] for c in available_skills if percentiles[c] >= 75]
    improvements = [_IMPROVE_LABELS[c] for c in available_skills if percentiles[c] < 50]

    # -- KNN similar players (same position preferred) ----------------------
    pos = str(player.get("position", ""))
    scope = df[df["position"] == pos] if (df["position"] == pos).sum() >= 10 else df
    scope = scope[scope["player_name"] != player["player_name"]].copy()

    similar_players: list[str] = []
    try:
        from sklearn.neighbors import NearestNeighbors
        from sklearn.preprocessing import StandardScaler

        feat = scope[available_skills].fillna(0).values
        if len(feat) >= 5:
            scaler = StandardScaler()
            X = scaler.fit_transform(feat)
            query = scaler.transform([player[available_skills].fillna(0).values])
            k = min(6, len(feat))
            nn = NearestNeighbors(n_neighbors=k, metric="euclidean")
            nn.fit(X)
            _, idxs = nn.kneighbors(query)
            similar_players = scope.iloc[idxs[0]]["player_name"].tolist()[:5]
    except Exception:
        # sklearn not available or edge case — skip silently
        pass

    # -- Profile card (single-row DataFrame) --------------------------------
    profile = {
        "Name":       player["player_name"],
        "Age":        int(player["age"]),
        "Nationality":player["nationality"],
        "Club":       player["club"],
        "Position":   player["position"],
        "Overall":    int(player["overall"]),
        "Potential":  int(player["potential"]),
        "Value":      _format_value(player["value_eur"]) if player["value_eur"] > 0 else "N/A",
        "Wage/wk":    _format_value(player["wage_eur"])  if player["wage_eur"]  > 0 else "N/A",
    }
    profile_df = pd.DataFrame([profile])

    # -- Skill snapshot (for radar chart) -----------------------------------
    skill_snapshot = {c.capitalize(): int(player.get(c, 0)) for c in available_skills}

    meta = {
        "title":           f"Scouting Report — {player['player_name']}",
        "intent":          "player_report",
        "player_name":     player["player_name"],
        "profile":         profile,
        "skill_snapshot":  skill_snapshot,
        "percentiles":     percentiles,
        "strengths":       strengths,
        "improvements":    improvements,
        "similar_players": similar_players,
        "player":          player,
    }
    return profile_df, meta
