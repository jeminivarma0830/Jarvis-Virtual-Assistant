"""
ui/server.py
Flask + SocketIO web dashboard for JARVIS.
Run with: python main.py --mode ui
Then open: http://localhost:5000
"""

import os
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from core.logger import get_logger

logger = get_logger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "jarvis-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

_jarvis = None   # set by start_server()


def start_server(jarvis_instance, port: int = None):
    global _jarvis
    _jarvis = jarvis_instance
    port = port or int(os.getenv("UI_PORT", 5000))
    logger.info(f"Dashboard available at http://localhost:{port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)


# ── HTTP Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400
    response = _jarvis.process(user_input)
    return jsonify({"response": response})


# ── SocketIO Events ──────────────────────────────────────────────────────────

@socketio.on("user_message")
def handle_message(data):
    user_input = data.get("message", "").strip()
    if not user_input:
        return
    # Process in background thread so socket isn't blocked
    def _process():
        response = _jarvis.process(user_input)
        socketio.emit("jarvis_response", {"message": response})
    threading.Thread(target=_process, daemon=True).start()
