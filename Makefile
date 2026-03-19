# Makefile for Bookstore Microservices

.PHONY: help build up down dev logs clean migrate test

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services in production mode"
	@echo "  down      - Stop all services"
	@echo "  dev       - Start all services in development mode (with auto-reload)"
	@echo "  logs      - Show logs for all services"
	@echo "  clean     - Remove all containers and images"
	@echo "  migrate   - Run migrations for all services"
	@echo "  test      - Run tests for all services"
	@echo ""
	@echo "Service-specific commands:"
	@echo "  logs-<service>    - Show logs for specific service"
	@echo "  shell-<service>   - Open shell in specific service"
	@echo "  migrate-<service> - Run migration for specific service"
	@echo ""
	@echo "Examples:"
	@echo "  make dev                    # Start development environment"
	@echo "  make logs-order-service     # Show order service logs"
	@echo "  make shell-order-service    # Open shell in order service"
	@echo "  make migrate-order-service  # Run order service migrations"

# Build all images
build:
	docker-compose build

# Start production environment
up:
	docker-compose up -d

# Start development environment with auto-reload
dev:
	docker-compose -f docker-compose.dev.yml up -d

# Stop all services
down:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Show logs for all services
logs:
	docker-compose logs -f

# Clean up containers and images
clean:
	docker-compose down -v --rmi all
	docker-compose -f docker-compose.dev.yml down -v --rmi all
	docker system prune -f

# Run migrations for all services
migrate:
	@echo "Running migrations for all services..."
	docker-compose run --rm customer-service python manage.py migrate
	docker-compose run --rm book-service python manage.py migrate
	docker-compose run --rm cart-service python manage.py migrate
	docker-compose run --rm staff-service python manage.py migrate
	docker-compose run --rm manager-service python manage.py migrate
	docker-compose run --rm catalog-service python manage.py migrate
	docker-compose run --rm order-service python manage.py migrate
	docker-compose run --rm ship-service python manage.py migrate
	docker-compose run --rm pay-service python manage.py migrate
	docker-compose run --rm comment-rate-service python manage.py migrate
	docker-compose run --rm recommend-ai-service python manage.py migrate
	docker-compose run --rm api-gateway python manage.py migrate

# Service-specific logs
logs-customer-service:
	docker-compose logs -f customer-service

logs-book-service:
	docker-compose logs -f book-service

logs-cart-service:
	docker-compose logs -f cart-service

logs-staff-service:
	docker-compose logs -f staff-service

logs-manager-service:
	docker-compose logs -f manager-service

logs-catalog-service:
	docker-compose logs -f catalog-service

logs-order-service:
	docker-compose logs -f order-service

logs-ship-service:
	docker-compose logs -f ship-service

logs-pay-service:
	docker-compose logs -f pay-service

logs-comment-rate-service:
	docker-compose logs -f comment-rate-service

logs-recommend-ai-service:
	docker-compose logs -f recommend-ai-service

logs-api-gateway:
	docker-compose logs -f api-gateway

# Service-specific shell access
shell-customer-service:
	docker-compose exec customer-service bash

shell-book-service:
	docker-compose exec book-service bash

shell-cart-service:
	docker-compose exec cart-service bash

shell-staff-service:
	docker-compose exec staff-service bash

shell-manager-service:
	docker-compose exec manager-service bash

shell-catalog-service:
	docker-compose exec catalog-service bash

shell-order-service:
	docker-compose exec order-service bash

shell-ship-service:
	docker-compose exec ship-service bash

shell-pay-service:
	docker-compose exec pay-service bash

shell-comment-rate-service:
	docker-compose exec comment-rate-service bash

shell-recommend-ai-service:
	docker-compose exec recommend-ai-service bash

shell-api-gateway:
	docker-compose exec api-gateway bash

# Service-specific migrations
migrate-customer-service:
	docker-compose run --rm customer-service python manage.py migrate

migrate-book-service:
	docker-compose run --rm book-service python manage.py migrate

migrate-cart-service:
	docker-compose run --rm cart-service python manage.py migrate

migrate-staff-service:
	docker-compose run --rm staff-service python manage.py migrate

migrate-manager-service:
	docker-compose run --rm manager-service python manage.py migrate

migrate-catalog-service:
	docker-compose run --rm catalog-service python manage.py migrate

migrate-order-service:
	docker-compose run --rm order-service python manage.py migrate

migrate-ship-service:
	docker-compose run --rm ship-service python manage.py migrate

migrate-pay-service:
	docker-compose run --rm pay-service python manage.py migrate

migrate-comment-rate-service:
	docker-compose run --rm comment-rate-service python manage.py migrate

migrate-recommend-ai-service:
	docker-compose run --rm recommend-ai-service python manage.py migrate

migrate-api-gateway:
	docker-compose run --rm api-gateway python manage.py migrate

# Development helpers
dev-build:
	docker-compose -f docker-compose.dev.yml build

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

dev-restart:
	docker-compose -f docker-compose.dev.yml restart

# Health check
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health/ || echo "API Gateway: DOWN"
	@curl -s http://localhost:8001/health/ || echo "Customer Service: DOWN"
	@curl -s http://localhost:8002/health/ || echo "Book Service: DOWN"
	@curl -s http://localhost:8003/health/ || echo "Cart Service: DOWN"
	@curl -s http://localhost:8004/health/ || echo "Staff Service: DOWN"
	@curl -s http://localhost:8005/health/ || echo "Manager Service: DOWN"
	@curl -s http://localhost:8006/health/ || echo "Catalog Service: DOWN"
	@curl -s http://localhost:8007/health/ || echo "Order Service: DOWN"
	@curl -s http://localhost:8008/health/ || echo "Ship Service: DOWN"
	@curl -s http://localhost:8009/health/ || echo "Pay Service: DOWN"
	@curl -s http://localhost:8010/health/ || echo "Comment Rate Service: DOWN"
	@curl -s http://localhost:8011/health/ || echo "Recommend AI Service: DOWN"