## help: Show this help message
.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'

# --------------------------------------
# Docker commands
# --------------------------------------

## build: Build Docker images
.PHONY: build
build:
	docker compose build

## up: Start Docker containers in detached mode
.PHONY: up
up:
	docker compose up -d

## down: Stop Docker containers
.PHONY: down
down:
	docker compose down

## restart: Restart containers
.PHONY: restart
restart: down up

# --------------------------------------
# Database commands
# --------------------------------------

## db-shell: Open Postgres shell
.PHONY: db-shell
db-shell:
	docker compose exec db psql -U postgres -d tenant_db

## migrate: Run Alembic migrations
.PHONY: migrate
migrate:
	docker compose exec api alembic upgrade head

.PHONY: wait-db
wait-db:
	@echo "Waiting for Postgres to be ready..."
	@until docker compose exec db pg_isready -U postgres; do \
		echo "Postgres not ready yet, waiting..."; \
		sleep 2; \
	done
	@echo "Postgres is ready!"

# --------------------------------------
# Logs
# --------------------------------------

## api-logs: Tail API container logs
.PHONY: api-logs
api-logs:
	docker compose logs -f api

## db-logs: Tail DB container logs
.PHONY: db-logs
db-logs:
	docker compose logs -f db

# --------------------------------------
# Combined commands
# --------------------------------------

## start: Build, start containers and run migrations
.PHONY: start
start: build up wait-db migrate
