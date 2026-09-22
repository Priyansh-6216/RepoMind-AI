# 🧠 RepoMind AI

> **AI-powered code intelligence platform** — Understand any GitHub repository with semantic search and grounded Q&A using RAG.

[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.3-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?logo=ollama&logoColor=white)](https://ollama.com)

---

## ✨ What It Does

Import any public GitHub repository and **ask questions about its codebase** — architecture, specific functions, design patterns, deployment flows. RepoMind AI uses **Retrieval-Augmented Generation (RAG)** to provide grounded, accurate answers backed by source code citations.

### Key Features

- 🏗️ **Intelligent Code Parsing** — AST-based chunking by function/class (not raw text)
- 🔍 **Semantic Vector Search** — pgvector cosine similarity over 768-dim embeddings
- 💬 **Grounded Q&A** — AI answers with file paths, line numbers, and relevance scores
- 📊 **Architecture Analysis** — Auto-generated architecture overviews
- 📖 **Onboarding Guides** — Developer onboarding summaries for any repo
- 🔄 **Flow Tracing** — Trace auth, payment, and custom flows through code
- 🆓 **100% Free** — Powered by Ollama (local LLM, no API costs)

---

## 🏛️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React (Vite)  │────▶│  Spring Boot API  │────▶│  Python Worker  │
│   Port 3000     │     │    Port 8080      │     │  Redis Consumer │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │     │                     │
                              ▼     ▼                     ▼
                        ┌──────┐ ┌──────┐          ┌──────────┐
                        │Redis │ │Ollama│          │  GitHub   │
                        │Queue │ │ LLM  │          │   API     │
                        └──────┘ └──────┘          └──────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  PostgreSQL      │
                     │  + pgvector      │
                     └──────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite | Interactive UI with chat interface |
| **Backend** | Spring Boot 3.3 (Java 17) | REST API, RAG orchestration |
| **Worker** | Python 3.11 | Repo cloning, AST parsing, embeddings |
| **Database** | PostgreSQL 16 + pgvector | Vector storage & similarity search |
| **Queue** | Redis 7 | Async job processing |
| **LLM** | Ollama (llama3.1 + nomic-embed-text) | Local, free inference |

---

## 🔄 How It Works

### Indexing Pipeline

```
1. User submits GitHub URL
2. Spring Boot creates job → Redis queue
3. Python worker consumes job:
   ├── Shallow git clone
   ├── Walk file tree (skip node_modules, .git, etc.)
   ├── AST-parse into semantic chunks (functions, classes)
   ├── Generate 768-dim embeddings via Ollama
   └── Store chunks + vectors in pgvector
4. Repository status → READY
```

### RAG Query Pipeline

```
1. User asks question
2. Spring Boot:
   ├── Generate query embedding (Ollama)
   ├── Cosine similarity search (pgvector, top-K=5)
   ├── Build grounded prompt with retrieved code
   ├── Generate answer (Ollama llama3.1)
   └── Return answer + source citations
```

---

## 🗃️ Database Schema

| Table | Description |
|-------|-------------|
| `repositories` | Tracked GitHub repos with status |
| `index_jobs` | Pipeline job tracking (QUEUED → COMPLETED) |
| `code_files` | Individual source files |
| `code_chunks` | Semantic chunks with 768-dim vector embeddings |
| `chat_sessions` | Conversation sessions per repo |
| `chat_messages` | Messages with JSONB citations |

---

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Docker & Docker Compose
- Ollama installed locally (for model downloads)

### 1. Clone & Configure

```bash
git clone https://github.com/Priyansh-6216/RepoMind-AI.git
cd RepoMind-AI
```

### 2. Pull Ollama Models

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

### 3. Launch All Services

```bash
docker-compose up --build
```

### 4. Open the App

Navigate to **http://localhost:3000**

---

## 🌍 Production Deployment

We've provided a fully automated deployment script for production environments. This leverages multi-stage builds, non-root users, memory limits, and the `prod` Spring profile.

1. SSH into your production server.
2. Clone the repository and configure your `.env` file (see `.env.example`).
3. Run the automated deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

This script will pull the latest code, inject environment variables, rebuild the optimized Docker images, and clean up any dangling resources!

---

## 📡 API Reference

### Repository Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/repos/import` | Import a GitHub repo |
| `GET` | `/api/repos` | List all repos |
| `GET` | `/api/repos/{id}` | Get repo details |
| `GET` | `/api/repos/{id}/status` | Get indexing status |
| `DELETE` | `/api/repos/{id}` | Delete repo |

### Chat Q&A

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/repos/{id}/chat` | Ask a question |
| `GET` | `/api/repos/{id}/chat/sessions` | List sessions |
| `GET` | `/api/repos/{id}/chat/sessions/{sid}` | Get messages |

### AI Insights

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/repos/{id}/insights/architecture` | Architecture overview |
| `POST` | `/api/repos/{id}/insights/onboarding` | Onboarding guide |
| `POST` | `/api/repos/{id}/insights/flow` | Flow tracing |

---

## 🗂️ Project Structure

```
RepoMind/
├── frontend/          # React + Vite
│   ├── src/
│   │   ├── components/   # Navbar, ChatPanel, CodeCitation ...
│   │   ├── pages/        # HomePage, RepoPage, ChatPage
│   │   ├── api/          # Axios client
│   │   └── index.css     # Design system
│   └── Dockerfile
│
├── backend/           # Spring Boot 3.3
│   └── src/main/java/com/repomind/
│       ├── controller/   # RepoController, ChatController, InsightController
│       ├── service/      # RepoService, ChatService, RAGService, InsightService
│       ├── model/        # JPA entities (6 tables)
│       ├── repository/   # Spring Data repos with native pgvector queries
│       ├── dto/          # Request/Response DTOs
│       └── config/       # Redis, CORS, Ollama configs
│
├── worker/            # Python 3.11
│   ├── main.py        # Redis consumer loop
│   ├── cloner.py      # Git clone
│   ├── parser.py      # File tree walker
│   ├── chunker.py     # AST-based code chunking
│   ├── embedder.py    # Ollama embedding generation
│   └── db.py          # pgvector storage
│
└── docker-compose.yml # Full stack orchestration
```

---

## 🧠 Key Design Decisions

1. **AST Chunking > Raw Text Splitting** — Python `ast` module for Python files, regex for Java/JS/TS. Each chunk is a meaningful code unit (function, class, method) rather than arbitrary 500-char blocks.

2. **Ollama over OpenAI** — Free, local, private. Uses `nomic-embed-text` (768-dim) for embeddings and `llama3.1` for generation. No API costs.

3. **pgvector Cosine Similarity** — IVFFlat index with 100 lists for fast approximate nearest neighbor search. Native SQL queries with the `<=>` distance operator.

4. **Redis Job Queue** — Decouples the API from heavy indexing work. Worker processes jobs asynchronously with progress tracking.

5. **Grounded Generation** — LLM receives only retrieved code context, not the full repo. Reduces hallucination and enables accurate source citations.

---

## 📝 Resume Line

> Built AI code intelligence platform using **Spring Boot + Python (LangChain) + pgvector + React**, enabling semantic search and grounded Q&A over GitHub repositories via RAG with AST-based code parsing and local LLM inference.

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.
