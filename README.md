# 🧠 LLM Debugging Copilot for Backend Systems

An LLM-powered system that analyzes backend logs across services to automatically identify root causes, correlate failures, and suggest actionable debugging steps.

---

## 🚀 Overview

This repo is a starter MVP that:
- loads JSON logs grouped by `request_id`
- bundles related logs into one incident
- sends that incident to an OpenAI model for analysis
- returns a structured debugging response

---

## 💡 Current Implementation

This project currently uses:
- Backend: Python, Flask
- LLM: OpenAI API
- Storage: JSON log files in `logs/`

The current flow is:
1. Generate sample logs with `scripts/generate_logs.py`
2. Start the Flask API in `backend/app.py`
3. Call `POST /analyze` with a `request_id`
4. Receive analysis from the OpenAI model

---

## ▶️ Setup & Run

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and configure:
   ```bash
   copy .env.example .env
   ```
   Update `.env`:
   ```text
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-small
   LOG_STORE_DIR=logs
   ```

4. Get a Gemini API key:
   - Sign up at https://makersuite.google.com/
   - Create an API key in your dashboard
   - Add it to your `.env` file

5. Generate sample logs:
   ```bash
   python scripts/generate_logs.py
   ```
   This creates `logs/sample_logs.json` with example incidents.

6. Start the Flask server:
   ```bash
   python backend/app.py
   ```

7. Open the web interface:
   - Visit `http://127.0.0.1:8000/` in your browser
   - Enter a `request_id` and click "Analyze"
   - Or test the API directly:
     ```bash
     curl -X POST http://127.0.0.1:8000/analyze \
       -H "Content-Type: application/json" \
       -d '{"request_id": "<one-of-generated-request-ids>"}'
     ```

---

## 📁 Project Files

- `backend/app.py` — main Flask API and OpenAI integration
- `scripts/generate_logs.py` — generates sample JSON logs
- `.env.example` — environment variable template
- `requirements.txt` — Python dependencies

---

## 🔧 What’s Left

The current project is an MVP. Remaining work includes:
- ingesting real production logs instead of synthetic examples
- adding a real log scraping or ingestion pipeline
- improving prompt engineering and response parsing
- adding validation and error reporting for log data
- writing tests for API and log processing
- adding deployment and production readiness documentation

---

## 🎯 Why This Project

- demonstrates how to apply LLMs for backend incident analysis
- uses log correlation to expose failure root cause
- provides a foundation to add real log ingestion later

---

## 👨‍💻 Author

Shivam Prasad
