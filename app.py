import os
import json
import warnings
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

warnings.filterwarnings("ignore", category=DeprecationWarning)

app = Flask(__name__, static_folder='.')
CORS(app)

HISTORY_FILE = "chat_history.json"
chat_history = []

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(chat_history, f)

def load_history():
    global chat_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            chat_history[:] = json.load(f)
    else:
        chat_history[:] = []

load_history()

def emotional_support_tool(query):
    responses = [
        "I'm here for you. It's okay to feel this way; many students have similar struggles.",
        "Remember, reaching out for help is a sign of strength.",
        "Taking deep breaths and giving yourself a break can help when things feel overwhelming."
    ]
    return responses[hash(query) % len(responses)]

def wellbeing_advice_tool(query):
    tips = [
        "Try a short walk or breathing exercise to clear your mind.",
        "Connect with a friend or family member for a quick chat.",
        "Break big tasks into smaller steps—celebrate each small win!"
    ]
    return tips[hash(query) % len(tips)]

# Simple tool invocation depending on keywords (basic example)
def get_tool_response(query):
    # You can expand this logic as needed
    if any(word in query.lower() for word in ["stress", "anxious", "sad", "depressed", "worry", "help"]):
        return emotional_support_tool(query)
    elif any(word in query.lower() for word in ["wellbeing", "tip", "advice", "health", "better"]):
        return wellbeing_advice_tool(query)
    else:
        return None

def call_ollama(prompt, model="llama3"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return "Sorry, there was a problem getting a response from the AI model."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    chat_history.append(("You", user_message))

    # Tool shortcut (optional, you can skip this if you want only LLM)
    tool_reply = get_tool_response(user_message)
    if tool_reply:
        bot_reply = tool_reply
    else:
        # Build prompt using history (optional: you can make this more sophisticated)
        previous = "\n".join([f"{s}: {t}" for s, t in chat_history[-10:]])  # last 10 exchanges
        prompt = f"You are a helpful mental health assistant.\n{previous}\nMindMate:"
        bot_reply = call_ollama(prompt)

    chat_history.append(("MindMate", bot_reply))
    save_history()
    return jsonify({"answer": bot_reply})

@app.route("/")
def index():
    return send_from_directory('.', "chat_page.html")

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

@app.route("/history", methods=["GET"])
def history():
    return jsonify([{"sender": sender, "text": text} for sender, text in chat_history])

if __name__ == "__main__":
    app.run(debug=True, port=8000)