from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return (
            "<h2>Banking API</h2>"
            "<p>OK. Try <code>/health</code> or <code>/api/echo?msg=hi</code>.</p>"
        )

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            time=datetime.now(timezone.utc).isoformat(),
        )

    @app.route("/api/echo", methods=["GET", "POST"])
    def echo():
        msg = request.args.get("msg")
        if msg is None and request.is_json:
            payload = request.get_json(silent=True) or {}
            msg = payload.get("msg")
        return jsonify(msg=msg, method=request.method)

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") not in {"0", "false", "False"}
    app.run(host=host, port=port, debug=debug)

