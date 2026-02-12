# Task Manager Backend API

A RESTful API backend for task management built with Flask, PostgreSQL, and containerized with Docker.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Application Flow](#application-flow)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security Features](#security-features)

## Overview

This backend service provides a complete task management API with CRUD operations, health monitoring, and comprehensive security scanning through an automated CI/CD pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│                    (Web Browser / Mobile App / API Client)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
│                         (Flask Application)                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    CORS     │  │    CSRF     │  │   Swagger   │  │   Error Handlers    │ │
│  │  Middleware │  │ Protection  │  │     UI      │  │   (404, 500)        │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API ROUTES                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────────┐ │
│  │  /api/tasks      │  │  /health         │  │  /api/csrf-token           │ │
│  │  GET, POST       │  │  Health Check    │  │  CSRF Token Generation     │ │
│  ├──────────────────┤  └──────────────────┘  └────────────────────────────┘ │
│  │  /api/tasks/<id> │                                                        │
│  │  PUT, DELETE     │                                                        │
│  └──────────────────┘                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      SQLAlchemy ORM                                      ││
│  │  ┌─────────────────────────────────────────────────────────────────┐    ││
│  │  │                      Task Model                                  │    ││
│  │  │  - id (Primary Key)                                              │    ││
│  │  │  - title (String, Required)                                      │    ││
│  │  │  - description (Text)                                            │    ││
│  │  │  - completed (Boolean)                                           │    ││
│  │  │  - created_at (DateTime)                                         │    ││
│  │  │  - updated_at (DateTime)                                         │    ││
│  │  └─────────────────────────────────────────────────────────────────┘    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE                                            │
│                        PostgreSQL                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Application Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           REQUEST FLOW                                        │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │ Client  │
    └────┬────┘
         │
         │  1. HTTP Request
         ▼
    ┌─────────────────┐
    │   Flask App     │
    │  (Port 5000)    │
    └────────┬────────┘
             │
             │  2. Middleware Processing
             ▼
    ┌─────────────────┐     ┌─────────────────┐
    │  CORS Check     │────▶│  CSRF Check     │
    └─────────────────┘     └────────┬────────┘
                                     │
                                     │  3. Route Matching
                                     ▼
                        ┌────────────────────────┐
                        │    Route Handler       │
                        │  (get/create/update/   │
                        │   delete task)         │
                        └───────────┬────────────┘
                                    │
                                    │  4. Database Operation
                                    ▼
                        ┌────────────────────────┐
                        │   SQLAlchemy ORM       │
                        └───────────┬────────────┘
                                    │
                                    │  5. SQL Query
                                    ▼
                        ┌────────────────────────┐
                        │     PostgreSQL         │
                        └───────────┬────────────┘
                                    │
                                    │  6. Response
                                    ▼
                        ┌────────────────────────┐
                        │   JSON Response        │
                        └───────────┬────────────┘
                                    │
                                    ▼
                              ┌─────────┐
                              │ Client  │
                              └─────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                        TASK CRUD OPERATIONS                                   │
└──────────────────────────────────────────────────────────────────────────────┘

  CREATE                    READ                     UPDATE                  DELETE
    │                        │                         │                       │
    ▼                        ▼                         ▼                       ▼
┌────────┐              ┌────────┐               ┌────────┐              ┌────────┐
│  POST  │              │  GET   │               │  PUT   │              │ DELETE │
│ /tasks │              │ /tasks │               │/tasks/ │              │/tasks/ │
└───┬────┘              └───┬────┘               │  {id}  │              │  {id}  │
    │                       │                    └───┬────┘              └───┬────┘
    ▼                       ▼                        ▼                       ▼
┌─────────┐            ┌─────────┐              ┌─────────┐            ┌─────────┐
│Validate │            │ Query   │              │  Find   │            │  Find   │
│  Input  │            │  All    │              │  Task   │            │  Task   │
└───┬─────┘            └───┬─────┘              └───┬─────┘            └───┬─────┘
    │                      │                        │                      │
    ▼                      ▼                        ▼                      ▼
┌─────────┐            ┌─────────┐              ┌─────────┐            ┌─────────┐
│ Create  │            │ Return  │              │ Update  │            │ Remove  │
│  Task   │            │  List   │              │ Fields  │            │  Task   │
└───┬─────┘            └───┬─────┘              └───┬─────┘            └───┬─────┘
    │                      │                        │                      │
    ▼                      ▼                        ▼                      ▼
┌─────────┐            ┌─────────┐              ┌─────────┐            ┌─────────┐
│  201    │            │  200    │              │  200    │            │  204    │
│ Created │            │   OK    │              │   OK    │            │No Content│
└─────────┘            └─────────┘              └─────────┘            └─────────┘
```

## API Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/api/tasks` | Get all tasks | - | `200` List of tasks |
| `POST` | `/api/tasks` | Create a task | `{title, description?, completed?}` | `201` Created task |
| `PUT` | `/api/tasks/<id>` | Update a task | `{title?, description?, completed?}` | `200` Updated task |
| `DELETE` | `/api/tasks/<id>` | Delete a task | - | `204` No content |
| `GET` | `/health` | Health check | - | `200` Status |
| `GET` | `/api/csrf-token` | Get CSRF token | - | `200` Token |
| `GET` | `/api/docs` | Swagger UI | - | Swagger documentation |

### Example Requests

**Create Task:**
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "My Task", "description": "Task details"}'
```

**Get All Tasks:**
```bash
curl http://localhost:5000/api/tasks
```

**Update Task:**
```bash
curl -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Delete Task:**
```bash
curl -X DELETE http://localhost:5000/api/tasks/1
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Flask 2.3.3 |
| Database ORM | Flask-SQLAlchemy 3.0.5 |
| Database | PostgreSQL |
| Migrations | Flask-Migrate 4.0.4 |
| CORS | Flask-Cors 4.0.0 |
| CSRF Protection | Flask-WTF 1.2.1 |
| API Documentation | Flask-Swagger-UI 4.11.1 |
| Testing | Pytest 7.4.0 |
| Container | Docker (Python 3.10-slim) |

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Docker (optional)

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/mahmoudsallem/Backend.git
cd Backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application:**
```bash
python app.py
```

### Docker Deployment

```bash
# Build image
docker build -t task-manager-backend .

# Run container
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  task-manager-backend
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Full PostgreSQL connection URL | Yes* |
| `POSTGRES_HOST` | Database host | Yes* |
| `POSTGRES_PORT` | Database port | Yes* |
| `POSTGRES_DB` | Database name | Yes* |
| `POSTGRES_USER` | Database user | Yes* |
| `POSTGRES_PASSWORD` | Database password | Yes* |
| `SECRET_KEY` | Flask secret key | Recommended |

*Either `DATABASE_URL` OR individual `POSTGRES_*` variables are required.

## CI/CD Pipeline

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           CI/CD PIPELINE FLOW                                 │
│                         (GitHub Actions)                                      │
└──────────────────────────────────────────────────────────────────────────────┘

  PR to dev                              Push to dev
     │                                       │
     ▼                                       ▼
┌─────────────┐                    ┌──────────────────┐
│   Stage 0   │                    │     Stage 1      │
│ Validation  │                    │ Credential Check │
│ - Dockerfile│                    │   (Gitleaks)     │
│ - app.py    │                    └────────┬─────────┘
│ - req.txt   │                             │
└─────────────┘                             ▼
                               ┌────────────────────────┐
                               │       Stage 2          │
                               │    SAST Analysis       │
                               │  ┌──────┬──────┬────┐  │
                               │  │Bandit│Semgrep│Snyk│ │
                               │  └──────┴──────┴────┘  │
                               │  ┌──────┬──────────┐   │
                               │  │Flake8│App Tests │   │
                               │  └──────┴──────────┘   │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │       Stage 3          │
                               │    Build Docker        │
                               │       Image            │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │       Stage 4          │
                               │    DAST Analysis       │
                               │  ┌──────┬──────┬────┐  │
                               │  │Trivy │ Snyk │ZAP │  │
                               │  │      │Cont. │    │  │
                               │  └──────┴──────┴────┘  │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │       Stage 5          │
                               │   Sign Image           │
                               │     (Cosign)           │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │       Stage 6          │
                               │  Update Helm Charts    │
                               │     (GitOps)           │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │       Summary          │
                               │  Pipeline Report       │
                               └────────────────────────┘
```

### Pipeline Stages

| Stage | Jobs | Purpose |
|-------|------|---------|
| 0 | File Validation | Verify required files exist (PR only) |
| 1 | Gitleaks | Scan for leaked secrets |
| 2 | Bandit, Semgrep, Snyk, Flake8, Tests | Static code analysis |
| 3 | Docker Build | Build container image |
| 4 | Trivy, Snyk Container, ZAP | Dynamic security testing |
| 5 | Cosign | Sign Docker image |
| 6 | Helm Update | Update Kubernetes manifests |

### Required Secrets

| Secret | Purpose |
|--------|---------|
| `SNYK_TOKEN` | Snyk vulnerability scanning |
| `HELM_REPO_PAT` | Access to Helm charts repository |

## Security Features

- **CSRF Protection**: All state-changing requests require CSRF token
- **CORS**: Configured cross-origin resource sharing
- **Input Validation**: Request data validation on all endpoints
- **Error Handling**: Secure error responses without sensitive data exposure
- **Secret Scanning**: Gitleaks prevents credential leaks
- **SAST**: Multiple static analysis tools (Bandit, Semgrep, Snyk)
- **DAST**: Dynamic testing with OWASP ZAP
- **Container Scanning**: Trivy and Snyk container analysis
- **Image Signing**: Cosign for supply chain security

## Project Structure

```
backend/
├── app.py                 # Main application
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── static/
│   └── swagger.json       # API documentation
├── tests/                 # Test files
├── .github/
│   ├── workflows/
│   │   ├── CICD.yaml      # Main CI/CD pipeline
│   │   └── pr-validation.yaml  # PR validation
│   ├── scripts/           # CI helper scripts
│   └── templates/         # Report templates
└── README.md
```

## License

This project is part of the NTI Final Project.

