# ScholarAI
Open-source AI-powered research assistant designed to help students and scientists navigate large volumes of academic literature. Supports paper discovery, summarization, citation exploration, and question answering across research papers. Helps organize knowledge, identify trends, and accelerate literature review workflows.

---

## ✨ Features

- PDF upload and indexing
- Retrieval-augmented question answering (RAG)
- Per-user data isolation (`user_id`)
- Local vector store with ChromaDB
- Simple web UI (HTML/CSS/JS)
- API-first backend (Flask)

---

## 🧱 Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **RAG:** LangChain + ChromaDB (local)
- **LLM:** Google Gemini

---

## 📁 Project Structure

```text
app/
  server.py              # Flask API + web routes
  pipeline.py            # Indexing + QA logic
  templates/
    index.html           # UI
  static/
    style.css
    app.js
temp/                    # Temporary uploaded files
```

---

## 🚀 Quick Start (Linux)

### 1) Clone and create virtual environment

```bash
git clone https://github.com/alphaonelabs/Alpha-one-labs-AI-research-assisstant.git
cd Alpha-one-labs-AI-research-assisstant
python3 -m venv venv
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

```bash
cp .env.example .env
```

Set in `.env`:

```env
GEMINI_API_KEY=your_key_here
```

### 4) Run locally

```bash
python -m app.server
```

If module run does not work in your setup:

```bash
python app/server.py
```

Open: `http://127.0.0.1:5000`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload + index PDF |
| `POST` | `/api/ask` | Ask a question |
| `DELETE` | `/api/user/<user_id>` | Delete user indexed data |

### `POST /api/upload`

- Content-Type: `multipart/form-data`
- Fields:
  - `pdf` (file)
  - `user_id` (string)

### `POST /api/ask`

```json
{
  "question": "What is the main contribution?",
  "user_id": "user_abc123"
}
```

---

## 🧪 Basic cURL Examples

```bash
curl -X GET http://127.0.0.1:5000/api/health
```

```bash
curl -X POST http://127.0.0.1:5000/api/upload \
  -F "pdf=@/path/to/paper.pdf" \
  -F "user_id=user_demo"
```

```bash
curl -X POST http://127.0.0.1:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Summarize section 2","user_id":"user_demo"}'
```

```bash
curl -X DELETE http://127.0.0.1:5000/api/user/user_demo
```

---

## 🤝 Contributing

We welcome contributions from the community.

1. Fork the repository
2. Create a feature branch  
   `git checkout -b feat/your-change`
3. Commit with clear messages
4. Open a Pull Request with:
   - Problem statement
   - What changed
   - Screenshots/logs (if UI or behavior changed)

Please open an issue first for large changes.

---

## ✅ PR Checklist

- [ ] Code runs locally
- [ ] Lint/tests pass
- [ ] No hardcoded secrets
- [ ] API/UI changes documented
- [ ] Small, focused PR

---

## 🛠 Troubleshooting

- **Upload returns 404:** frontend must call `POST /api/upload` (not `/upload`).
- **Upload says invalid file:** request field name must be `pdf` (not `file`).
- **Ask fails:** ensure `user_id` and `question` are both sent.
- **No model response:** verify `GEMINI_API_KEY` is set correctly.

---

## 🔐 Security

- Do not commit `.env` or API keys.
- Rotate keys if exposed.
- Use `DELETE /api/user/<user_id>` to remove user data.

---

## 📄 License

See [LICENSE](LICENSE).

---

## 🙌 Maintained by

**Alpha One Labs**  
Open-source AI tooling for practical research workflows.