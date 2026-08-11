# PRD — URL Shortener with CI/CD Pipeline

## 1. Purpose
App logic stays minimal. Real objective: demonstrate a solid CI pipeline — build, quality-gate, containerize, push to registry.

## 2. Tech Stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python), served via `uvicorn` |
| Env | Python `venv` (local dev) |
| Database | MySQL 8, running as Docker container |
| Containerization | Docker |
| Code Quality | SonarQube (self-hosted or SonarCloud) |
| Image Registry | Docker Hub |
| CI/CD | GitHub Actions |

No frontend. No JWT/auth on the API — out of scope, adds no pipeline value.

## 3. Functional Scope

### 3.1 API Endpoints
| Method | Route | Description |
|---|---|---|
| POST | `/shorten` | Accepts long URL + optional `custom_alias` + optional `expires_at`, returns short code |
| POST | `/shorten/bulk` | Accepts array of URLs, returns array of short codes (loops single-shorten logic, no new code path) |
| GET | `/{short_code}` | Redirects to original URL (302). Returns 410 if expired |
| GET | `/qr/{short_code}` | Returns QR code image for the short URL |
| GET | `/stats/{short_code}` | Returns click count, created_at, expires_at |
| GET | `/health` | Health check endpoint |

**Deliberately excluded to keep debugging simple:** rate limiting (middleware/state adds config and debug overhead disproportionate to resume value), per-click analytics log (extra table + join on every redirect — a single counter column is enough).

### 3.2 What Goes Into MySQL
Everything that needs to persist goes to DB — no in-memory store:
- `id` (PK, auto increment)
- `short_code` (unique, indexed) — either user-supplied custom alias or auto-generated
- `original_url`
- `created_at`
- `expires_at` (nullable — null means no expiry)
- `click_count` (single integer, incremented on each redirect — no separate log table)

Table: `urls`. Still a single table — custom alias and expiry are just extra columns, not extra structure.

## 4. Database Design

### 4.1 Users
Two MySQL users — separation of privilege, not just for show:

| User | Role | Privileges |
|---|---|---|
| `root` | Admin/init only | Full — used only for container init, schema migration, DB creation. Never used by the app. |
| `url_app_user` | Application runtime | `SELECT, INSERT, UPDATE` on `shortener_db.*` only. No `DROP`, no `ALTER`, no admin grants. |

### 4.2 Config
- MySQL runs as a Docker container (official `mysql:8` image)
- Root password + app user credentials via env vars — **never hardcoded, never committed**. This is exactly what SonarQube secret-scanning will flag if you get lazy.
- Separate `.env` for local dev (venv + local MySQL container)

## 5. CI/CD Pipeline (GitHub Actions)

### Trigger
On push/PR to `main`.

### Stage 1 — CI
1. Checkout code
2. Setup Python venv, install deps
3. Lint (flake8/ruff)
4. Run unit tests (pytest)

### Stage 2 — Code Quality Gate
5. SonarQube scan
6. **Pipeline fails if quality gate fails** — not decorative, actually blocking

### Stage 3 — Build & Push
7. Docker build, tag with `git SHA` (not `latest` — you need traceable rollback)
8. Push image to Docker Hub

Pipeline ends here for now.

## 6. Non-Functional Requirements
- No secrets in code/repo — enforced by SonarQube + `.gitignore`
- Image tags immutable (SHA-based)
- Pipeline must fail loudly on any gate failure (lint, test, sonar) — no soft-pass

## 7. Out of Scope
- Authentication/authorization on API
- Frontend UI
- Custom domain / analytics dashboard
- Deployment (any target) — no CD stage right now

## 8. Deliverables for Resume/README
- Architecture diagram (FastAPI → MySQL, pipeline flow)
- GitHub Actions run screenshot (CI + SonarQube gate + Docker Hub push)
- SonarQube report screenshot
- Docker Hub repo screenshot (pushed image with SHA tag)
