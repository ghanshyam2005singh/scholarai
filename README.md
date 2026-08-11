# ScholarAI

Open-source AI-powered research assistant by Alpha One Labs.
Ask research questions, summarise papers, discover literature, and generate reviews —
all powered by **Cloudflare Workers AI** (`@cf/meta/llama-3.1-8b-instruct-fp8`).

---

## Project Structure

```text
scholarai/
├── src/
│   └── worker.py       # Single Python Worker — routing + AI logic
├── static/
│   └── index.html      # Full frontend (HTML/CSS/JS, no build step)
├── wrangler.toml        # Cloudflare Workers config
└── README.md
```

---

## Quick Start

### Prerequisites

- A free [Cloudflare account](https://dash.cloudflare.com/sign-up)
- [Node.js and npm](https://nodejs.org/)

Install Wrangler locally in the project before running the commands below:

```bash
npm i -D wrangler@latest
```

See Cloudflare's [Wrangler installation guide](https://developers.cloudflare.com/workers/wrangler/install-and-update/) for installation and update details.

### 1. Log in to Cloudflare

```bash
npx wrangler login
```

### 2. Run locally

```bash
npx wrangler dev
```

Opens at `http://localhost:8787`.

### 3. Deploy

```bash
npx wrangler deploy
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
