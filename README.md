<div align="center">

# 🔗 URL Shortener — CI/CD to ECS

**A minimal FastAPI URL shortener built to showcase a production-grade CI/CD pipeline —**
**lint → test → SonarQube → Docker Hub → AWS ECS.**

*The shortener is the excuse. The pipeline is the point.*

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![AWS ECS](https://img.shields.io/badge/AWS-ECS-FF9900?style=flat-square&logo=amazonecs&logoColor=white)
![SonarQube](https://img.shields.io/badge/SonarQube-Quality%20Gate-4E9BCD?style=flat-square&logo=sonarqube&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

</div>

---

## 🚀 What this is

A single-table URL shortener API — custom aliases, expiry, QR codes, bulk shorten, click tracking.
No auth, no rate limiting, no analytics tables — deliberately minimal, so the pipeline stays the focus, not the app.

Every push to `main` triggers a full pipeline: **lint → test + coverage → SonarQube quality gate → Docker build & push → ECS rolling deploy.**

---

## 🧩 Pipeline Architecture

### 1️⃣ CI Pipeline — `ci.yml`

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 60, 'rankSpacing': 80, 'curve': 'basis'}, 'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    A["🐙 <b>GitHub</b><br/>push → main"] --> B["🐍 <b>flake8</b><br/>Lint app/ + tests/"]
    B --> C["🧪 <b>pytest + coverage</b><br/>Run test suite"]
    C --> D["📦 <b>Upload Artifact</b><br/>coverage.xml"]
    D --> E["🔍 <b>SonarQube</b><br/>Static analysis scan"]
    E --> F{"🚦 <b>Quality Gate</b><br/>Pass or fail?"}
    F -- "❌ fail" --> X["🛑 <b>Pipeline Stopped</b><br/>No image built"]
    F -- "✅ pass" --> G["🐳 <b>Docker Buildx</b><br/>Build image"]
    G --> H["🔐 <b>Docker Hub</b><br/>Push :sha + :latest"]

    style A fill:#24292e,stroke:#fff,stroke-width:2px,color:#fff
    style B fill:#3776AB,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#0A9EDC,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#5c5c5c,stroke:#fff,stroke-width:2px,color:#fff
    style E fill:#4E9BCD,stroke:#fff,stroke-width:2px,color:#fff
    style F fill:#F5A623,stroke:#333,stroke-width:2px,color:#000
    style X fill:#D93025,stroke:#fff,stroke-width:2px,color:#fff
    style G fill:#2496ED,stroke:#fff,stroke-width:2px,color:#fff
    style H fill:#0db7ed,stroke:#fff,stroke-width:2px,color:#fff
```

### 2️⃣ CD Pipeline — `cd.yml` *(triggers automatically when CI succeeds)*

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 60, 'rankSpacing': 80, 'curve': 'basis'}, 'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    I["⚡ <b>GitHub Actions</b><br/>workflow_run: CI success"] --> J["☁️ <b>AWS Auth</b><br/>Configure credentials"]
    J --> K["📝 <b>Render Task Def</b><br/>Inject new image tag"]
    K --> L["🚀 <b>Amazon ECS</b><br/>Deploy to main-cluster"]
    L --> M["🔄 <b>Rolling Update</b><br/>Zero-downtime swap"]
    M --> N["✅ <b>Service Stable</b><br/>Health checks pass"]

    style I fill:#2088FF,stroke:#fff,stroke-width:2px,color:#fff
    style J fill:#FF9900,stroke:#333,stroke-width:2px,color:#000
    style K fill:#FF9900,stroke:#333,stroke-width:2px,color:#000
    style L fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:#FF9900
    style M fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:#FF9900
    style N fill:#2EA44F,stroke:#fff,stroke-width:2px,color:#fff
```

### 🔑 Icon Legend

| Icon | Tool | Role in the pipeline |
|:---:|---|---|
| 🐙 | **GitHub** | Trigger — push to `main` |
| 🐍 | **flake8** | Lint `app/` + `tests/` |
| 🧪 | **pytest / coverage** | Unit tests + coverage report |
| 📦 | **Actions Artifact** | Carries coverage.xml into the Sonar job |
| 🔍 | **SonarQube** | Static analysis + quality gate |
| 🐳 | **Docker Buildx** | Build the image |
| 🔐 | **Docker Hub** | Image registry (SHA-tagged + `latest`) |
| ⚡ | **GitHub Actions** | `workflow_run` links CI → CD |
| ☁️ | **AWS IAM** | Auth for ECS deploy |
| 🚀 | **Amazon ECS** | Task definition render + rolling deploy |

| **Deploy** | AWS ECS | Renders new task definition, rolling deploy, waits for service stability |

---

## ⚙️ Tech Stack

| Layer | Choice |
|---|---|
| API | FastAPI + Pydantic v2 |
| ORM | SQLAlchemy 2.0 |
| DB | MySQL 8 (containerized) |
| QR Codes | `qrcode[pil]` |
| Local dev | Docker Compose |
| CI | GitHub Actions |
| Code quality | flake8 + SonarQube |
| Registry | Docker Hub |
| Deployment | AWS ECS (Fargate/EC2 via task definition) |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/shorten` | Shorten a single URL (optional custom alias + expiry) |
| `POST` | `/shorten/bulk` | Shorten multiple URLs in one call |
| `GET` | `/{short_code}` | Redirect to original URL (302 / 404 / 410 if expired) |
| `GET` | `/stats/{short_code}` | Click count + metadata for a short code |
| `GET` | `/qr/{short_code}` | PNG QR code for the short URL |
| `GET` | `/health` | Health check (verifies DB connectivity) |

---

## 🏃 Run it locally

```bash
git clone https://github.com/ArshadKhan-007/URL-SHORTENER-CI-CD-ECS.git
cd URL-SHORTENER-CI-CD-ECS
cp .env.example .env      # fill in DB credentials
docker compose up --build
```

App is live at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

```bash
# Example: shorten a URL
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/some/very/long/path"}'
```

---

## 🔐 CI/CD Secrets Required

| Secret | Used by |
|---|---|
| `SONAR_TOKEN`, `SONAR_HOST_URL` | SonarQube scan + quality gate |
| `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` | Docker image push |
| `AWS_ACCESS_KEY`, `AWS_SECRET_KEY` | ECS deploy |

---

## 📁 Project Structure

```
.
├── app/                  # FastAPI application
│   ├── main.py           # Routes (6 endpoints)
│   ├── models.py         # SQLAlchemy ORM
│   ├── schemas.py        # Pydantic request/response models
│   ├── crud.py
│   ├── database.py
│   └── config.py
├── tests/                # pytest suite
├── db/init.sh            # MySQL init script
├── .github/workflows/
│   ├── ci.yml             # lint → test → sonar → docker push
│   └── cd.yml             # ECS rolling deploy on CI success
├── task-definition.json   # ECS task definition
├── docker-compose.yml     # local dev stack
└── Dockerfile
```

---
