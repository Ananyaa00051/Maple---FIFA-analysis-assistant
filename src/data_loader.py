"""
data_loader.py
Handles loading, validation, cleaning, and caching of the FIFA dataset.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path


REQUIRED_COLUMNS = [
    "player_name", "age", "nationality", "club", "position",
    "overall", "potential", "value_eur", "wage_eur",
    "pace", "shooting", "passing", "dribbling", "defending", "physicality"
]

COLUMN_ALIASES = {
    # Common alternative names in FIFA CSVs
    "short_name": "player_name",
    "long_name": "player_name",
    "name": "player_name",
    "club_name": "club",
    "nationality_name": "nationality",
    "player_positions": "position",
    "physic": "physicality",
    "value_eur": "value_eur",
    "wage_eur": "wage_eur",
}


def load_dataset(path: str = "data/fifa_players.csv") -> pd.DataFrame:
    """Load the FIFA CSV dataset and return a cleaned DataFrame."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. "
            "Please place your FIFA CSV file at data/fifa_players.csv"
        )

    df = pd.read_csv(file_path, low_memory=False)
    df = _normalize_columns(df)
    df = validate_dataset(df)
    df = clean_dataset(df)
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and strip column names, apply aliases."""
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    for alias, canonical in COLUMN_ALIASES.items():
        if alias in df.columns and canonical not in df.columns:
            df.rename(columns={alias: canonical}, inplace=True)

    # Take first position if multiple listed (e.g. "ST, CF")
    if "position" in df.columns:
        df["position"] = df["position"].astype(str).str.split(",").str[0].str.strip()

    return df


def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Check required columns exist; raise informative errors if not."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        available = ", ".join(df.columns.tolist()[:20])
        raise ValueError(
            f"Required column(s) missing: {', '.join(missing)}.\n"
            f"Available columns: {available}"
        )
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and type-cast the dataset:
    - Numeric coercion
    - Fill missing skill stats with 0
    - Drop rows without player_name or overall
    - Reset index
    """
    numeric_cols = [
        "age", "overall", "potential", "value_eur", "wage_eur",
        "pace", "shooting", "passing", "dribbling", "defending", "physicality"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with no name or overall rating
    df = df.dropna(subset=["player_name", "overall"])

    # Fill missing skill values with 0 (e.g. GK pace)
    skill_cols = ["pace", "shooting", "passing", "dribbling", "defending", "physicality"]
    df[skill_cols] = df[skill_cols].fillna(0)

    # Fill value/wage with 0 if missing
    df["value_eur"] = df["value_eur"].fillna(0)
    df["wage_eur"] = df["wage_eur"].fillna(0)

    df["age"] = df["age"].fillna(0).astype(int)
    df["overall"] = df["overall"].astype(int)
    df["potential"] = df["potential"].fillna(df["overall"]).astype(int)

    df = df.reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_cached_dataset(path: str = "data/fifa_players.csv") -> pd.DataFrame:
    """Streamlit-cached version of load_dataset."""
    return load_dataset(path)


def get_dataset_info(df: pd.DataFrame) -> dict:
    """Return summary statistics for sidebar display."""
    return {
        "total_players": len(df),
        "total_clubs": df["club"].nunique(),
        "total_nationalities": df["nationality"].nunique(),
        "avg_overall": round(df["overall"].mean(), 1),
        "avg_potential": round(df["potential"].mean(), 1),
        "positions": sorted(df["position"].dropna().unique().tolist()),
    }
