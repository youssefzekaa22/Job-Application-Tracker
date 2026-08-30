# Job Application Tracker

A small web app for tracking job applications: which company, which role, when you applied, and where each one stands. It replaces the spreadsheet most people end up keeping, and it shows response rates so you can tell which applications are actually going somewhere.

Built as a two-container stack — a Flask app and a PostgreSQL database — orchestrated with Docker Compose.

---

## Features

- Add applications with company, position, status, link, and notes
- Update status inline: `applied` → `interview` → `offer` / `rejected`
- Dashboard stats: total applications, interviews, response rate
- Data survives container restarts and rebuilds

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Python 3.11, Flask |
| Database | PostgreSQL 16 |
| Containerization | Docker, Docker Compose |

---

## Running It

**Requirements:** Docker and Docker Compose.

```bash
git clone https://github.com/youssefzekaa22/job-tracker.git
cd job-tracker

cp .env.example .env
# fill in POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

docker compose up -d
```

Open `http://localhost:5000`.

To stop:

```bash
docker compose down       # keeps your data
docker compose down -v    # deletes the volume and all data
```

---

## Configuration

All configuration is passed at runtime through environment variables — nothing is baked into the image.

| Variable | Purpose |
|---|---|
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_DB` | Database name |
| `DB_HOST` | Database hostname — matches the Compose service name |
| `APP_PORT` | Port the Flask app listens on |

`.env` is gitignored. `.env.example` documents the required keys without exposing values.

---

## Docker Implementation Notes

The containerization is the substance of this project, so the decisions behind it are worth spelling out.

### Multi-stage build

The build stage runs on the full `python:3.11` image, which carries the compilers some Python packages need at install time. The runtime stage starts fresh from `python:3.11-slim` and copies over only the installed packages. Build tooling never reaches the final image.

### Non-root execution

The container creates a dedicated user and switches to it before the application starts. Installed packages are relocated into that user's home directory with ownership set at copy time, and `PATH` is adjusted to match — a root-owned package directory would otherwise be unreadable to the app.

### Network isolation

The database service publishes no ports. It is reachable only from inside the Compose network, over Docker's internal DNS, using the service name as its hostname. `docker compose ps` shows the difference: the app has a `->` port mapping, the database does not.

### Data persistence

Database files live in a named volume rather than the container's writable layer, so the application can be rebuilt or replaced without touching the data.

### Health-check-gated startup

`depends_on` alone only guarantees that a container has *started*, not that it is *ready*. PostgreSQL takes a few seconds to initialize, and an app that connects during that window crashes. The database defines a `pg_isready` health check, and the app waits on `service_healthy` — which removes the race condition rather than working around it with a retry loop.

The app also exposes `/health`, which opens a real database connection before reporting healthy, so a failure downstream is visible rather than silent.

### Build context hygiene

`.dockerignore` keeps secrets, git history, and local artifacts out of the build context entirely. Deleting a file in a later layer does not remove it from the image — the only reliable approach is keeping it out from the start.

---

## Project Structure

```
job-tracker/
├── app.py                 # Flask application
├── requirements.txt       # Pinned dependencies
├── Dockerfile             # Multi-stage build
├── docker-compose.yml     # Service orchestration
├── .dockerignore
├── .gitignore
├── .env.example
└── README.md
```

---

## Author

**Youssef Zakaria** — [GitHub](https://github.com/youssefzekaa22) · [LinkedIn](https://www.linkedin.com/in/youssef-zakaria-8a8252276)
