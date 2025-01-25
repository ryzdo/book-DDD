# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker compose build

up:
	docker compose up -d postgres

down:
	docker compose down

start:
	docker compose start postgres

stop:
	docker compose stop

test:
	uv run pytest --tb=short
