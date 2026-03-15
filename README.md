# ScholarAI

Open-source AI-powered research assistant by Alpha One Labs.
Ask research questions, summarise papers, discover literature, and generate reviews —
all powered by **Cloudflare Workers AI** (`@cf/meta/llama-3.1-8b-instruct`).

---

## Project Structure

```
scholarai/
├── src/
│   └── worker.py       # Single Python Worker — routing + AI logic
├── static/
│   └── index.html      # Full frontend (HTML/CSS/JS, no build step)
├── wrangler.jsonc       # Cloudflare Workers config
├── package.json         # npm scripts for Wrangler CLI
└── README.md
```

---

## Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) ≥ 18
- A free [Cloudflare account](https://dash.cloudflare.com/sign-up)

### 1. Install Wrangler

```bash
npm install
npx wrangler login
```

### 2. Run locally

```bash
npm run dev
```

Opens at `http://localhost:8787`.

### 3. Deploy

```bash
npm run deploy
```

---

## API Endpoints

| Method | Endpoint         | Description                    |
|--------|-----------------|-------------------------------|
| GET    | `/`             | Serves the frontend HTML       |
| GET    | `/api/health`   | Health check                   |
| POST   | `/api/ask`      | Ask a research question        |
| POST   | `/api/summarize`| Summarise a paper              |
| POST   | `/api/discover` | Discover relevant papers       |
| POST   | `/api/review`   | Generate a literature review   |

### `POST /api/ask`

```json
{ "question": "What is transfer learning?", "context": "(optional excerpt)" }
```

### `POST /api/summarize`

```json
{ "title": "...", "abstract": "...", "content": "..." }
```

At least one field required.

### `POST /api/discover`

```json
{ "query": "graph neural networks", "fields": ["ML", "biology"], "limit": 10 }
```

### `POST /api/review`

```json
{ "topic": "self-supervised learning", "style": "comprehensive", "audience": "researchers" }
```

`style` options: `comprehensive`, `brief`, `systematic`

---

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-change`
3. Commit and open a Pull Request with a clear description

Please open an issue first for large changes.

---

## License

See [LICENSE](LICENSE).

---

## Maintained by

**Alpha One Labs** — open-source AI tooling for practical research workflows.