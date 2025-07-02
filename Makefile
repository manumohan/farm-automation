# Makefile for Farm Automation Platform

.PHONY: up down logs install-backend install-frontend prune

up: install-backend install-frontend
	docker compose -f docker/docker-compose.yml up --build -d backend frontend mosquitto mqtt-web-client mqtt-status-worker

install-backend:
	cd backend && pip install -r requirements.txt || true

install-frontend:
	cd frontend && npm install || true

down:
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f 

prune:
	docker system prune -a -f 