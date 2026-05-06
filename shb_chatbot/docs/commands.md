# Commands Reference

This project provides commands via two interfaces: **Make** targets for common
workflows and a **project CLI** for fine-grained control.

## Make Commands

Run these from the project root directory.

### Quick Start

| Command | Description |
|---------|-------------|
| `make quickstart` | Install deps, start Docker, run migrations, create admin user |
| `make install` | Install backend dependencies with uv + pre-commit hooks |

### Development

| Command | Description |
|---------|-------------|
| `make run` | Start development server with hot reload |
| `make run-prod` | Start production server (0.0.0.0:8000) |
| `make routes` | Show all registered API routes |
| `make test` | Run tests with verbose output |
| `make test-cov` | Run tests with coverage report (HTML + terminal) |
| `make format` | Auto-format code with ruff |
| `make lint` | Lint and type-check code (ruff + ty) |
| `make clean` | Remove cache files (__pycache__, .pytest_cache, etc.) |

### Database

| Command | Description |
|---------|-------------|
| `make db-init` | Start PostgreSQL + create initial migration + apply |
| `make db-migrate` | Create new migration (prompts for message) |
| `make db-upgrade` | Apply pending migrations |
| `make db-downgrade` | Rollback last migration |
| `make db-current` | Show current migration revision |
| `make db-history` | Show full migration history |

### Users

| Command | Description |
|---------|-------------|
| `make create-admin` | Create admin user (interactive) |
| `make user-create` | Create new user (interactive) |
| `make user-list` | List all users |

### Celery

| Command | Description |
|---------|-------------|
| `make celery-worker` | Start Celery worker |
| `make celery-beat` | Start Celery beat scheduler |
| `make celery-flower` | Start Flower monitoring UI (port 5555) |

### Docker (Development)

| Command | Description |
|---------|-------------|
| `make docker-up` | Start all backend services |
| `make docker-down` | Stop all services |
| `make docker-logs` | Follow backend logs |
| `make docker-build` | Build backend images |
| `make docker-shell` | Open shell in app container |
| `make docker-frontend` | Start frontend (separate compose) |
| `make docker-frontend-down` | Stop frontend |
| `make docker-frontend-logs` | Follow frontend logs |
| `make docker-frontend-build` | Build frontend image |
| `make docker-db` | Start only PostgreSQL |
| `make docker-db-stop` | Stop PostgreSQL |
| `make docker-redis` | Start only Redis |
| `make docker-redis-stop` | Stop Redis |

### Docker (Production with Traefik)

| Command | Description |
|---------|-------------|
| `make docker-prod` | Start production stack |
| `make docker-prod-down` | Stop production stack |
| `make docker-prod-logs` | Follow production logs |
| `make docker-prod-build` | Build production images |

### Vercel (Frontend Deployment)

| Command | Description |
|---------|-------------|
| `make vercel-deploy` | Deploy frontend to Vercel |

---

## Project CLI

All project CLI commands are invoked via:

```bash
cd backend
uv run shb_chatbot <group> <command> [options]
```

### Server Commands

```bash
uv run shb_chatbot server run              # Start dev server
uv run shb_chatbot server run --reload     # With hot reload
uv run shb_chatbot server run --port 9000  # Custom port
uv run shb_chatbot server routes           # Show all registered routes
```

### Database Commands

```bash
uv run shb_chatbot db init                  # Run all migrations
uv run shb_chatbot db migrate -m "message"  # Create new migration
uv run shb_chatbot db upgrade               # Apply pending migrations
uv run shb_chatbot db upgrade --revision e3f  # Upgrade to specific revision
uv run shb_chatbot db downgrade             # Rollback last migration
uv run shb_chatbot db downgrade --revision base  # Rollback to start
uv run shb_chatbot db current               # Show current revision
uv run shb_chatbot db history               # Show migration history
```

### User Commands

```bash
# Create user (interactive prompts for email/password)
uv run shb_chatbot user create

# Create user non-interactively
uv run shb_chatbot user create --email user@example.com --password secret

# Create user with specific role
uv run shb_chatbot user create --email admin@example.com --password secret --role admin

# Create user with superuser flag
uv run shb_chatbot user create --email admin@example.com --password secret --superuser

# Create admin (shortcut)
uv run shb_chatbot user create-admin --email admin@example.com --password secret

# Change user role
uv run shb_chatbot user set-role user@example.com --role admin

# List all users
uv run shb_chatbot user list
```

### Celery Commands

```bash
uv run shb_chatbot celery worker                    # Start worker
uv run shb_chatbot celery worker --loglevel debug   # Debug logging
uv run shb_chatbot celery worker --concurrency 8    # 8 worker processes
uv run shb_chatbot celery beat                      # Start scheduler
uv run shb_chatbot celery flower                    # Start Flower UI
uv run shb_chatbot celery flower --port 5556        # Custom Flower port
```

### Custom Commands

Custom commands are auto-discovered from `app/commands/`. Run them via:

```bash
uv run shb_chatbot cmd <command-name> [options]
```

## Adding Custom Commands

Commands are auto-discovered from `app/commands/`. Create a new file:

```python
# app/commands/my_command.py
import click
from app.commands import command, success, error

@command("my-command", help="Description of what this does")
@click.option("--name", "-n", required=True, help="Name parameter")
def my_command(name: str):
    """Your command logic here."""
    success(f"Done: {name}")
```

Run it:

```bash
uv run shb_chatbot cmd my-command --name test
```

For more details, see `docs/adding_features.md`.
