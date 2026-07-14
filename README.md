# HCP CRM — AI-First Interaction Logging Module

An AI-powered Customer Relationship Management module for pharmaceutical/life sciences field representatives to log, edit, and manage interactions with Healthcare Professionals (HCPs). Built with a dual-input design: a structured form and a conversational AI chat interface that auto-populates the same form.

## Objective

This project conceptualizes the "Log Interaction Screen" of an AI-first CRM's HCP module. Field reps can log meetings, calls, and other HCP interactions either by filling out a structured form manually, or by describing the interaction in plain natural language to an AI assistant, which extracts and populates the relevant fields automatically using an LLM-powered LangGraph agent.

## Tech Stack

- **Frontend:** React + Redux
- **Backend:** Python + FastAPI
- **AI Agent Framework:** LangGraph
- **LLM:** Groq API — `gemma2-9b-it` (primary), `llama-3.3-70b-versatile` (secondary/fallback)
- **Database:** SQLite (via Python's built-in `sqlite3`, no ORM) — chosen for zero-setup local development; schema is designed to be portable to PostgreSQL/MySQL for production
- **Font:** Google Inter

## Features

- **Structured Form:** HCP name, interaction type, date/time, attendees, topics discussed, materials shared, samples distributed, HCP sentiment (Positive/Neutral/Negative), outcomes, and follow-up actions
- **AI Chat Assistant:** Log interactions by typing a natural-language summary (e.g. *"Met Dr. Sarah Chen, discussed OncoBoost efficacy and left a sample"*) — the agent extracts structured data and fills the form automatically
- **AI Suggested Follow-ups:** Context-aware next-best-action suggestions generated after each interaction is logged

## LangGraph Agent & Tools

The agent orchestrates 5 tools to manage the full interaction lifecycle:

| Tool | Description |
|---|---|
| `log_interaction` | Parses free-text (chat) input, uses the LLM to extract HCP name, interaction type, topics, materials, sentiment, and outcomes, then creates a new interaction record |
| `edit_interaction` | Takes an HCP name or interaction reference plus a natural-language edit instruction, locates the correct existing record, and updates it |
| `suggest_followups` | Generates 2-3 relevant next-best-action suggestions based on the logged interaction's content |
| `search_hcp_history` | Retrieves past logged interactions for a given HCP; returns a friendly message if no history exists |
| `materials_lookup` | Searches available materials/samples by topic keyword; returns a friendly message if no match is found |

## Project Structure
hcp-crm-log-interaction/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entrypoint
│   │   ├── database.py       # SQLite connection + table setup (init_db)
│   │   ├── api/               # REST endpoints (hcps, interactions, materials, chat)
│   │   └── agent/
│   │       ├── graph.py       # LangGraph agent definition
│   │       └── tools.py       # 5 agent tools
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/        # Form panel, chat panel
│   │   ├── redux/             # State management
│   │   └── App.jsx
│   └── package.json
└── README.md


## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/keys)

### 1. Clone the repository
```bash
git clone https://github.com/mithunj7999-cyber/hcp-crm-log-interaction.git
cd hcp-crm-log-interaction
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in `backend/` (copy from `.env.example`):

GROQ_API_KEY=your_groq_api_key_here
Run the backend:
```bash
uvicorn app.main:app --reload
```
Backend runs at `http://127.0.0.1:8000` — API docs available at `http://127.0.0.1:8000/docs`. Database tables are created automatically on first run.

### 3. Frontend setup
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`.

## Usage

1. Open the app in your browser (`http://localhost:5173`)
2. **Structured form:** fill in interaction details manually on the left panel
3. **AI Assistant:** on the right panel, type a natural-language description of an interaction (e.g. *"Met Dr. Sarah Chen, discussed OncoBoost efficacy and left a sample"*) — the form auto-populates
4. Review AI-suggested follow-ups and click to add them
5. To edit a logged interaction, describe the change in chat (e.g. *"Edit my interaction with Dr. Sarah Chen — change sentiment to negative"*)

## Notes

- SQLite is used for local development speed; the schema is structured for easy migration to PostgreSQL/MySQL in production
- CORS is enabled for all origins in this dev build — restrict this before any production deployment
- Built as a technical assignment demonstrating an AI-first CRM interaction logging workflow

## Author

Mithun J
[GitHub](https://github.com/mithunj7999-cyber) | [LinkedIn](https://linkedin.com/in/mithun-j-84645a380)