# ⚽ MAPLE

### Match & Athlete Performance and League Evaluator

MAPLE is an AI-powered football analytics assistant built on FIFA player data. It allows users to ask natural language questions about football players and teams and receive structured insights, rankings, comparisons, and analytics.

---

## 🎥 Demo

Loom Walkthrough:
https://www.loom.com/share/c205efeffc9b491aafdbe60bd72e7953

---

## Features

* Top player rankings
* Player comparisons
* Young talent discovery
* Advanced player filtering
* Team-level analytics
* Best value player analysis
* AI-generated insights using Groq LLM
* Interactive visualizations

---

## Example Queries

* Show me the top 10 players by overall rating
* Find the best young players under age 23
* Compare Messi and Ronaldo
* Show me the best strikers with pace above 85
* Which teams have the highest average player rating?
* Give me a short analysis of the best value players

---

## Tech Stack

* Python
* Streamlit
* Pandas
* Plotly
* Groq API (Llama 3.3 70B)

---

## Architecture

```text
User Query
     │
     ▼
Streamlit Interface
     │
     ▼
Groq LLM
(Intent Extraction)
     │
     ▼
Intent Router
     │
     ├── Ranking Engine
     ├── Filtering Engine
     ├── Comparison Engine
     ├── Team Analytics Engine
     └── Value Analysis Engine
     │
     ▼
Pandas Data Processing
     │
     ▼
Structured Results
(Table / Charts)
     │
     ▼
Groq Insight Generator
     │
     ▼
Final Response
```

---

## Query Processing Pipeline

1. User submits a natural language football query.
2. Groq extracts the intent and relevant parameters.
3. The Intent Router maps the request to the appropriate analytics function.
4. Pandas performs filtering, ranking, aggregation, or comparison on the FIFA dataset.
5. Results are displayed as structured tables and visualizations.
6. Groq generates concise insights based on the retrieved results.
7. The final response is presented to the user.

### Example

**User Query**

> Show me the best strikers with pace above 85

**Intent Extracted**

```json
{
  "intent": "filter_players",
  "position": "ST",
  "pace_min": 85
}
```

**Analytics Execution**

```python
df[
    (df["position"] == "ST") &
    (df["pace"] > 85)
].sort_values("overall", ascending=False)
```

**Output**

* Ranked player table
* Interactive chart
* AI-generated insight summary

---

## Dataset

**FIFA 23 Complete Player Dataset**

The dataset contains player information and performance attributes, including:

* Name
* Age
* Nationality
* Club
* Position
* Overall Rating
* Potential
* Market Value
* Wage
* Pace
* Shooting
* Passing
* Dribbling
* Defending
* Physicality

---

## Project Structure

```text
maple/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── fifa_players.csv
│
├── src/
│   ├── data_loader.py
│   ├── query_parser.py
│   ├── intent_router.py
│   ├── analytics.py
│   ├── llm_service.py
│   ├── visualization.py
│   └── utils.py
│
├── screenshots/
│
└── assets/
```

---

## Running Locally

### 1. Clone the Repository

```bash
git clone <repository-url>
cd maple
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
```

### 4. Start the Application

```bash
streamlit run app.py
```

---

## AI Usage

Groq LLM is used for:

* Natural language query understanding
* Intent extraction
* Query parameter identification
* Insight generation and result summarization

All calculations, filtering, aggregations, rankings, and comparisons are performed directly on the FIFA dataset using Pandas.

---

## Limitations

* Works only with the provided FIFA dataset
* Does not provide live football statistics
* Query support is limited to implemented analytics features
* Player comparisons require matching names present in the dataset

---

## Author

Built for IQM internship assignment task
