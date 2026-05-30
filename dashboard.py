"""
ui/dashboard.py  –  Optional Flask web dashboard with real-time updates via SocketIO
Run:  python ui/dashboard.py
Then open:  http://localhost:5000
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.brain   import Brain
from core.speech  import Speaker
from memory.long_term import Memory

app    = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*")

memory  = Memory()
brain   = Brain(memory=memory)
speaker = Speaker()

chat_history = []   # [{role, text}, ...]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("message", "").strip()
    if not user_text:
        return jsonify({"error": "empty message"}), 400

    reply = brain.think(user_text)
    chat_history.append({"role": "user",      "text": user_text})
    chat_history.append({"role": "assistant",  "text": reply})

    # Push to all connected browser clients
    socket.emit("new_message", {"role": "assistant", "text": reply})

    # Speak in background thread so HTTP response isn't delayed
    threading.Thread(target=speaker.speak, args=(reply,), daemon=True).start()

    return jsonify({"reply": reply})


@app.route("/api/history")
def history():
    return jsonify(chat_history)


@app.route("/api/reset", methods=["POST"])
def reset():
    brain.reset()
    chat_history.clear()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("🌐  Dashboard running at http://localhost:5000")
    socket.run(app, host="0.0.0.0", port=5000, debug=False)
