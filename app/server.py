import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

try:
    from app.pipeline import index_document, ask_question, delete_user_data
except Exception:
    from pipeline import index_document, ask_question, delete_user_data

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR.parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "scholarai-mvp"})


@app.post("/api/upload")
def upload_pdf():
    pdf = request.files.get("pdf")
    user_id = request.form.get("user_id", "").strip()

    if not user_id:
        return jsonify({"ok": False, "error": "user_id is required"}), 400
    if not pdf or not pdf.filename.lower().endswith(".pdf"):
        return jsonify({"ok": False, "error": "Valid PDF file is required"}), 400

    temp_file = TEMP_DIR / f"{uuid.uuid4()}_{secure_filename(pdf.filename)}"
    pdf.save(temp_file)

    try:
        meta = index_document(str(temp_file), user_id=user_id)
        return jsonify({"ok": True, "message": "PDF indexed", **meta})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)


@app.post("/api/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    user_id = (data.get("user_id") or "").strip()

    if not user_id or not question:
        return jsonify({"ok": False, "error": "user_id and question are required"}), 400

    try:
        answer = ask_question(question, user_id=user_id)
        return jsonify({"ok": True, "answer": answer})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.delete("/api/user/<user_id>")
def delete_user(user_id: str):
    try:
        data = delete_user_data(user_id)
        return jsonify({"ok": True, **data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)