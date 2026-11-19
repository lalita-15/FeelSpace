
# FeelSpace 🌿

A community platform where users can share their thoughts and feelings in a welcoming digital space.

## Overview

FeelSpace is a Flask-based web application backed by PostgreSQL. It provides user authentication and a community space for sharing thoughts.

The project is also being developed as a hands-on Cloud and DevOps portfolio project.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL 18
- **Database Driver:** Psycopg
- **Authentication:** Flask Sessions, Werkzeug Password Hashing
- **Application Server:** Gunicorn
- **Containerization:** Docker
- **Container Orchestration (current setup):** Docker Compose

## Features

- User registration and login
- Password hashing
- Session-based authentication
- Community thought sharing
- REST API for thoughts
- Application health endpoint
- PostgreSQL database integration

## Project Structure

```text
FeelSpace/
├── .env.example
├── .gitignore
├── README.md
└── feelspace/
    ├── app.py
    ├── db.py
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── static/
    └── templates/
```

## Run with Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/lalita-15/FeelSpace.git
cd FeelSpace
```

### 2. Configure environment variables

Create your own `.env` file using `.env.example`.

Set your own SECRET_KEY and DB_PASSWORD values.

### 3. Start the application

```bash
cd feelspace
docker compose --env-file ..\.env up -d --build
```

### 4. Access the application

Open:

http://localhost:5002

### 5. Check container status

```bash
docker compose --env-file ..\.env ps
```

## Database Persistence

PostgreSQL uses a Docker named volume:

`feelspace-postgres-data`

This keeps database data persistent across container restarts.

## DevOps Roadmap

- [x] Flask application containerization
- [x] PostgreSQL containerization
- [x] Docker Compose integration
- [x] Database persistent storage
- [ ] GitHub Actions CI/CD
- [ ] Docker image publishing
- [ ] Kubernetes deployment
- [ ] Kubernetes ConfigMaps and Secrets
- [ ] Persistent Volumes and Claims
- [ ] Health probes and self-healing
- [ ] Autoscaling
- [ ] AWS deployment
- [ ] Monitoring and logging

## Author

**Lalita Rajpoot**

GitHub: https://github.com/lalita-15
