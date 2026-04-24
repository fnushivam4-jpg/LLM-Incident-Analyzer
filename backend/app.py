import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-small")
LOG_STORE_DIR = os.getenv("LOG_STORE_DIR", "logs")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY must be set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)


def load_incident_logs(request_id: str) -> list:
    """Load logs from JSON files and return entries matching request_id."""
    entries = []

    if not os.path.isdir(LOG_STORE_DIR):
        return entries

    for filename in os.listdir(LOG_STORE_DIR):
        if not filename.lower().endswith(".json"):
            continue

        path = os.path.join(LOG_STORE_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            continue

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("request_id") == request_id:
                    entries.append(item)
        elif isinstance(data, dict):
            if data.get("request_id") == request_id:
                entries.append(data)

    return entries


def build_analysis_prompt(request_id: str, logs: list) -> str:
    """Create a prompt for the LLM to analyze the bundled incident logs."""
    prompt_lines = [
        f"Analyze the backend incident for request_id: {request_id}.",
        "You are an expert backend debugging assistant.",
        "Use the logs to identify the root cause, supporting evidence, and actionable next steps.",
        "Return output as JSON with keys: root_cause, evidence, and next_steps.",
        "",
        "Incident logs:",
    ]

    for index, log in enumerate(logs, start=1):
        prompt_lines.append(f"--- Log entry {index} ---")
        prompt_lines.append(json.dumps(log, indent=2, ensure_ascii=False))

    return "\n".join(prompt_lines)


def analyze_logs_with_llm(request_id: str, logs: list) -> dict:
    """Send the prompt to Gemini and return a structured analysis."""
    prompt = build_analysis_prompt(request_id, logs)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=2048,
        ),
    )

    content = response.text
    return {
        "request_id": request_id,
        "analysis": content,
        "log_count": len(logs),
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze_request():
    payload = request.get_json(force=True, silent=True) or {}
    request_id = payload.get("request_id")

    if not request_id:
        return jsonify({"error": "request_id is required in JSON body."}), 400

    logs = load_incident_logs(request_id)
    if not logs:
        return jsonify({"error": f"No logs found for request_id {request_id}."}), 404

    try:
        analysis = analyze_logs_with_llm(request_id, logs)
        return jsonify(analysis)
    except Exception as exc:
        return jsonify({"error": "Failed to analyze logs.", "details": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=True)
