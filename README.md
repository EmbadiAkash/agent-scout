# 🧭 AgentScout — Anakin Forge Hackathon

AgentScout is an autonomous AI job-research agent built for the Anakin Forge Hackathon.

## What it does

A user provides:

- target role
- location
- important skills
- work mode
- experience level

AgentScout then:

1. Builds a research objective.
2. Uses the official Anakin Python SDK to search the live web.
3. Reads the returned web evidence.
4. Scores each result against the user's requirements.
5. Ranks the opportunities.
6. Gives the user a direct action link to inspect/apply.

## Why this is an agent

This is not only a chatbot. It performs a multi-step workflow:

**Understand → Research → Read → Reason/Score → Recommend → Act**

## Where Anakin is used

Anakin is the live-web intelligence layer. The app calls Anakin's Search API through the official Python SDK to research current opportunities and retrieve web evidence. The application then reasons over those results using the user's preferences.

Anakin's official SDK exposes `client.search(...)`, and the Search API is designed for AI-powered web search with structured results. See the official Anakin documentation.

## Tech stack

- Python
- Streamlit
- Anakin Python SDK
- Anakin Search API
- python-dotenv

## Run locally

### 1. Install Python 3.10+

Check:

```bash
python --version
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install packages

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy `.env.example` to `.env` and put your Anakin API key in it:

```text
ANAKIN_API_KEY=ak-your-real-key
```

Never upload `.env` to GitHub.

### 5. Run

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select your GitHub repository.
5. Main file: `app.py`
6. Add a secret:

```toml
ANAKIN_API_KEY = "ak-your-real-key"
```

7. Deploy.

## Hackathon submission

Project title:

**AgentScout — Autonomous AI Job Research Agent**

Project description:

**AgentScout is an agentic AI application that helps users discover and prioritize current job opportunities. It converts a user's role, location, skills, experience, and work-mode preferences into a live web research task, uses Anakin to search and read web information, evaluates the returned evidence, ranks opportunities against the user's requirements, and provides direct action links. The stack uses Python, Streamlit, the official Anakin Python SDK, and Anakin Search API.**

## Important

Do not commit API keys, passwords, or private credentials.
