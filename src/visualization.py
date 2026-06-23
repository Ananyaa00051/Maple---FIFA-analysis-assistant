"""
visualization.py
Plotly chart builders for the FIFA Scout Assistant.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


ACCENT = "#00D4A4"       # teal-green
BG = "rgba(0,0,0,0)"    # transparent background
GRID = "rgba(255,255,255,0.08)"
TEXT = "#E8EDF2"
BAR_COLORS = [
    "#00D4A4", "#00B8D4", "#0085FF", "#7C5CBF", "#D45B00",
    "#D4A400", "#D40054", "#54D400", "#4400D4", "#D44400",
]


def _base_layout(title: str) -> dict:
    return dict(
        title=dict(text=title, font=dict(color=TEXT, size=15, family="Inter, sans-serif")),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT, family="Inter, sans-serif", size=12),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    )


# ---------------------------------------------------------------------------
# 1. Top Players Bar Chart
# ---------------------------------------------------------------------------

def chart_top_players(result_df: pd.DataFrame, title: str = "Top Players by Overall Rating"):
    """Horizontal bar chart of player overall ratings."""
    if result_df.empty or "Player" not in result_df.columns:
        return None

    df = result_df.copy()
    # Use up to top 15
    df = df.head(15).iloc[::-1]  # Reverse for ascending display

    fig = go.Figure(go.Bar(
        x=df["Overall"],
        y=df["Player"],
        orientation="h",
        marker=dict(
            color=df["Overall"],
            colorscale=[[0, "#0085FF"], [0.5, "#00B8D4"], [1, "#00D4A4"]],
            showscale=False,
        ),
        text=df["Overall"],
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))

    layout = _base_layout(title)
    layout["height"] = max(300, len(df) * 30 + 80)
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 2. Top Clubs Bar Chart
# ---------------------------------------------------------------------------

def chart_top_clubs(result_df: pd.DataFrame, title: str = "Top Clubs by Average Rating"):
    """Horizontal bar chart for team/club analysis."""
    if result_df.empty or "Club" not in result_df.columns:
        return None

    df = result_df.copy()
    metric_col = "Avg Overall" if "Avg Overall" in df.columns else df.columns[2]
    df = df.head(15).iloc[::-1]

    fig = go.Figure(go.Bar(
        x=df[metric_col],
        y=df["Club"],
        orientation="h",
        marker=dict(
            color=list(range(len(df))),
            colorscale=[[0, "#7C5CBF"], [0.5, "#0085FF"], [1, "#00D4A4"]],
            showscale=False,
        ),
        text=df[metric_col].round(1),
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))

    layout = _base_layout(title)
    layout["height"] = max(300, len(df) * 30 + 80)
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 3. Age vs Overall Scatter Plot
# ---------------------------------------------------------------------------

def chart_age_vs_overall(df: pd.DataFrame, highlight_df: pd.DataFrame | None = None):
    """Scatter plot of age vs overall for context, with highlighted players."""
    sample = df.sample(min(1500, len(df)), random_state=42)

    fig = go.Figure()

    # Background scatter
    fig.add_trace(go.Scatter(
        x=sample["age"],
        y=sample["overall"],
        mode="markers",
        marker=dict(color="rgba(0,180,255,0.15)", size=4),
        name="All Players",
        hoverinfo="skip",
    ))

    # Highlighted players
    if highlight_df is not None and not highlight_df.empty and "Player" in highlight_df.columns:
        merged = highlight_df.merge(df[["player_name", "age"]], left_on="Player", right_on="player_name", how="left")
        if "Overall" in merged.columns and "age" in merged.columns:
            fig.add_trace(go.Scatter(
                x=merged["age"],
                y=merged["Overall"],
                mode="markers+text",
                text=merged["Player"],
                textposition="top center",
                textfont=dict(size=9, color=ACCENT),
                marker=dict(color=ACCENT, size=10, line=dict(color="white", width=1)),
                name="Results",
            ))

    layout = _base_layout("Age vs Overall Rating")
    layout.update(dict(
        xaxis=dict(title="Age", gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(title="Overall Rating", gridcolor=GRID, zerolinecolor=GRID),
        height=380,
        showlegend=False,
    ))
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 4. Player Comparison Radar Chart
# ---------------------------------------------------------------------------

RADAR_METRICS = ["pace", "shooting", "passing", "dribbling", "defending", "physicality"]


def chart_player_comparison(meta: dict):
    """Radar / spider chart comparing two players."""
    p1 = meta.get("p1")
    p2 = meta.get("p2")
    players = meta.get("players", [])

    if p1 is None or p2 is None or len(players) < 2:
        return None

    categories = [m.capitalize() for m in RADAR_METRICS] + [RADAR_METRICS[0].capitalize()]

    def vals(row):
        return [int(row.get(m, 0)) for m in RADAR_METRICS] + [int(row.get(RADAR_METRICS[0], 0))]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=vals(p1), theta=categories,
        fill="toself", name=players[0],
        line=dict(color=ACCENT),
        fillcolor="rgba(0,212,164,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals(p2), theta=categories,
        fill="toself", name=players[1],
        line=dict(color="#FF6B6B"),
        fillcolor="rgba(255,107,107,0.15)",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID, color=TEXT),
            angularaxis=dict(gridcolor=GRID, color=TEXT),
        ),
        paper_bgcolor=BG,
        font=dict(color=TEXT, family="Inter, sans-serif"),
        legend=dict(font=dict(color=TEXT)),
        title=dict(text=meta.get("title", "Player Comparison"), font=dict(color=TEXT, size=14)),
        height=420,
        margin=dict(l=60, r=60, t=60, b=40),
    )
    return fig


# ---------------------------------------------------------------------------
# 5. Value Score Bar Chart
# ---------------------------------------------------------------------------

def chart_value_players(result_df: pd.DataFrame):
    """Bar chart for hidden gems by value score."""
    if result_df.empty or "Value Score" not in result_df.columns:
        return None

    df = result_df.head(10).iloc[::-1]

    fig = go.Figure(go.Bar(
        x=df["Value Score"],
        y=df["Player"],
        orientation="h",
        marker=dict(color=ACCENT),
        text=df["Value Score"].round(3),
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))

    layout = _base_layout("Best Value Players (Score = (Overall+Potential) / Market Value)")
    layout["height"] = max(300, len(df) * 35 + 80)
    fig.update_layout(**layout)
    return fig
