# ⚽ FIFA AI Scout Assistant

An AI-powered football analytics chatbot that lets you ask natural language questions about FIFA player and team data — and get ranked tables, interactive charts, and Groq-powered insights in return.

---

## 🌟 Features

| Feature | Description |
|---|---|
| **Top Players** | Rank players by overall rating, globally or by position |
| **Young Talent** | Discover rising stars under any age threshold |
| **Player Comparison** | Head-to-head radar charts & stat tables |
| **Advanced Filtering** | Filter by pace, nationality, club, position, and more |
| **Team Analysis** | Club rankings by average overall or potential |
| **Hidden Gems** | Undervalued players by value score formula |
| **High Potential** | Future stars sorted by potential rating |
| **AI Summaries** | Groq LLaMA 3.3 generates 3-bullet insights for every result |
| **Interactive Charts** | Plotly bar charts, scatter plots, radar charts |

---

## 📦 Dataset

**Recommended:** [FIFA 23 Complete Player Dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset) from Kaggle.

**Expected CSV columns:**

```
player_name, age, nationality, club, position, overall, potential,
value_eur, wage_eur, pace, shooting, passing, dribbling, defending, physicality
```

The loader auto-normalizes common column name variants (e.g. `short_name` → `player_name`, `physic` → `physicality`).

**Don't have the dataset yet?** Generate a 600-player sample for testing:

```bash
uv run python generate_sample_data.py
```

---

## 🛠️ Quick Start (with `uv` — recommended)

[`uv`](https://docs.astral.sh/uv/) is a blazing-fast Python package manager. It replaces `pip` + `venv` in a single tool.

### 1. Install `uv` (one-time)

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the repository

```bash
git clone https://github.com/your-username/fifa-ai-scout.git
cd fifa-ai-scout/fifa_scout
```

### 3. Create environment & install all dependencies

```bash
uv sync
```

> This automatically creates a `.venv/` folder and installs every dependency pinned in `uv.lock`. No manual `pip install` needed.

### 4. Add your dataset

```
fifa_scout/
└── data/
    └── fifa_players.csv    ← place your CSV here
```

Or generate sample data:

```bash
uv run python generate_sample_data.py
```

### 5. Set your API key

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

**Or** copy the secrets template:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit it and add your key
```

### 6. Run the app

```bash
uv run streamlit run app.py
```

The app opens at **http://localhost:8501** ⚡

---

## 🛠️ Alternative: pip (classic)

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
streamlit run app.py
```

---

## 🔑 Groq API Setup

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create a free API key
3. Paste it into your `.env` or `.streamlit/secrets.toml`

The app uses **`llama-3.3-70b-versatile`** for both query parsing and summary generation.

---

## 💬 Example Queries

```
Show me top 10 players
Compare Messi and Ronaldo
Best players under 23
Best strikers with pace above 85
Which clubs have the highest average rating?
Best value players
Players with potential above 90
Top 5 goalkeepers
Spanish players with overall above 85
Best midfielders under 25
```

---

## 🏗️ Architecture

```
User Query (natural language)
        │
        ▼
┌─────────────────────┐
│   Query Parser      │  ← Groq LLM classifies intent → JSON
│   (query_parser.py) │
└────────┬────────────┘
         │  {intent, filters, limit, ...}
         ▼
┌─────────────────────┐
│   Intent Router     │  ← Dispatches to correct function
│   (intent_router.py)│
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Analytics Engine  │  ← Pure Pandas operations
│   (analytics.py)    │
└────────┬────────────┘
         │  DataFrame + metadata
         ▼
┌─────────────────────┐    ┌──────────────────────┐
│   Visualization     │    │   LLM Summary        │
│   (visualization.py)│    │   (llm_service.py)   │
└────────┬────────────┘    └──────────┬───────────┘
         │                            │
         └──────────┬─────────────────┘
                    ▼
         Streamlit Chat UI (app.py)
```

---

## 📁 Folder Structure

```
fifa_scout/
│
├── app.py                   # Streamlit app entry point
├── pyproject.toml           # uv / pip project metadata & deps
├── requirements.txt         # pip fallback
├── uv.lock                  # Pinned dependency lockfile (uv)
├── README.md
├── generate_sample_data.py  # Test data generator
├── .env                     # Your API key (git-ignored)
├── .gitignore
│
├── data/
│   └── fifa_players.csv     # Your FIFA dataset
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py       # CSV loading, validation, caching
│   ├── query_parser.py      # Groq intent classification
│   ├── intent_router.py     # Intent → analytics function routing
│   ├── analytics.py         # All Pandas analytics logic
│   ├── llm_service.py       # Groq client + summary generation
│   ├── visualization.py     # Plotly chart builders
│   └── utils.py             # Shared helpers
│
└── .streamlit/
    ├── config.toml          # Dark theme config
    └── secrets.toml.example
```

---

## 🤖 AI Usage Explanation

The app uses Groq's LLaMA 3.3 70B model in **two distinct ways**:

### 1. Query Understanding (Intent Classification)
The LLM reads the user's natural language question and returns **only a structured JSON object** — it never answers football questions directly. This JSON specifies the intent type (`top_players`, `compare_players`, etc.) and extracted parameters (filters, limits, player names). This keeps analytics deterministic and data-grounded.

### 2. Result Summarization
After Pandas computes the result table, a **data snapshot** (max 30 rows) is sent to the LLM with a strict prompt: summarize in 3 bullet points, max 80 words, no hallucinations, use only provided data. This produces grounded, factual insights rather than generic football commentary.

---

## ⚠️ Known Limitations

- **Dataset-dependent:** Accuracy depends on the quality and completeness of your FIFA CSV. Missing columns (e.g. `pace`) will raise a clear error.
- **Player name matching:** Uses substring matching — very common names (e.g. "Fernandez") may match the wrong player.
- **GK stats:** FIFA stores goalkeeper-specific ratings separately; pace/shooting/etc. are often 0 for GKs in some exports.
- **Value scores:** Hidden gems formula (`(overall + potential) / value_eur`) favours cheap players — very low-value players may score unrealistically high.
- **Groq rate limits:** Free tier has request limits. Heavy usage may require a paid plan.
- **No real-time data:** Dataset is static — reflects the FIFA version of your CSV, not live transfer market values.
- **Multi-player comparison:** Currently supports exactly 2 players. Comparing 3+ is not yet implemented.
