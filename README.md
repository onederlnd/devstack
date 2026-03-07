# ⬡ Devstack

A Reddit/Twitter hybrid social platform for developers. Built with Flask, SQLite, and Docker.

## Features
- Post and reply to developer discussions
- Vote, bookmark, and follow other developers
- Topic channels (e.g. `/t/python`)
- Full-text search across posts and topics
- Personalized feed from followed users

## Tech Stack
- **Backend:** Python, Flask
- **Database:** SQLite with FTS5 full-text search
- **Frontend:** Jinja2, Vanilla JS
- **DevOps:** Docker, GitHub Actions CI

## Getting Started

### Prerequisites
- Python 3.13+
- Docker & Docker Compose

### Local Setup
```bash
# clone the repo
git clone https://github.com/onederlnd/devstack.git
cd devstack

# create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements-dev.txt

# create .env file
cp .env.example .env

# run the app
python run.py
```

App runs at `http://localhost:5000`

### Running with Docker
```bash
sudo docker-compose up
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Dev Scripts
| Command | Description |
|---------|-------------|
| `./scripts/feature.sh` | Start a new feature branch |
| `./scripts/ship.sh` | Run tests, lint, commit, and push |
| `./scripts/done.sh` | Clean up after a PR is merged |
| `./scripts/help.sh` | Print workflow reference |

### Branching Workflow
1. `./scripts/feature.sh` — create a feature branch
2. Write code and tests
3. `./scripts/ship.sh` — commit and push
4. Open a PR on GitHub
5. Review and merge
6. `./scripts/done.sh` — return to main and clean up

## Project Structure
```
devstack/
├── app/
│   ├── __init__.py        # app factory
│   ├── models/            # database access
│   ├── routes/            # flask blueprints
│   ├── templates/         # jinja2 templates
│   └── static/            # css and js
├── tests/                 # pytest test suite
├── scripts/               # dev workflow scripts
├── Dockerfile
├── docker-compose.yml
└── run.py
```

## CI
GitHub Actions runs tests and linting on every push. See `.github/workflows/ci.yml`.