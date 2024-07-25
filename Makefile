.PHONY: up down clean clean_volumes clean_orphans clean_images clean_all re build_all up_nginx up_backend up_db up_elk up_all up_no_elk logs_nginx logs_backend logs_db logs_elk status exec_nginx exec_backend exec_db exec_elk stop_all help

# Default target: Build and start all services except ELK stack
all: up_no_elk

# Build all Docker images
build_all:
	docker-compose -f ./docker-compose.yml build

# Start all services except ELK stack and rebuild if necessary
up_no_elk:
	docker-compose -f ./docker-compose.yml up --build -d nginx backend_dummy db

# Start all services including ELK stack and rebuild if necessary
up_all:
	docker-compose -f ./docker-compose.yml up --build -d

# Start specific services and rebuild if necessary
up_nginx:
	docker-compose -f ./docker-compose.yml up --build -d nginx

up_backend:
	docker-compose -f ./docker-compose.yml up --build -d backend_dummy

up_db:
	docker-compose -f ./docker-compose.yml up --build -d db

up_elk:
	docker-compose -f ./docker-compose.yml up --build -d es01 kibana logstash01 filebeat01 metricbeat01

# Stop and remove containers, networks, and volumes
down:
	docker-compose -f ./docker-compose.yml down

# Clean up volumes
# Use this to remove volumes and reset persistent data
clean_volumes:
	docker-compose -f ./docker-compose.yml down -v

# Clean up orphans
# Use this to remove containers that are no longer defined in the current docker-compose.yml
clean_orphans:
	docker-compose -f ./docker-compose.yml down --remove-orphans

# Clean up images
# Use this to remove all Docker images
clean_images:
	docker rmi -f $$(docker images -aq)

# Clean up all: containers, networks, volumes, and images
# Use this for a full cleanup of the Docker environment
clean_all: clean_volumes clean_orphans clean_images

# Clean up: containers, networks, volumes, and orphans (default clean)
# Use this to reset data and ensure only defined services are running
clean: clean_volumes clean_orphans

# Rebuild and start all services
re: clean_all up_no_elk

# Tail logs from specific services
logs_nginx:
	docker-compose -f ./docker-compose.yml logs -f nginx

logs_backend:
	docker-compose -f ./docker-compose.yml logs -f backend_dummy

logs_db:
	docker-compose -f ./docker-compose.yml logs -f db

logs_elk:
	docker-compose -f ./docker-compose.yml logs -f es01 kibana logstash01 filebeat01 metricbeat01

# Check status of running containers
status:
	docker-compose -f ./docker-compose.yml ps

# Open a shell in a specific container
exec_nginx:
	docker-compose -f ./docker-compose.yml exec nginx sh

exec_backend:
	docker-compose -f ./docker-compose.yml exec backend_dummy sh

exec_db:
	docker-compose -f ./docker-compose.yml exec db sh

exec_elk:
	docker-compose -f ./docker-compose.yml exec es01 sh

# Stop all services without removing them
stop_all:
	docker-compose -f ./docker-compose.yml stop

# Show help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all            Build and start all services except ELK stack"
	@echo "  up_no_elk      Build and start all services except ELK stack"
	@echo "  up_all         Build and start all services including ELK stack"
	@echo "  up_nginx       Build and start only the Nginx service"
	@echo "  up_backend     Build and start only the backend service"
	@echo "  up_db          Build and start only the database service"
	@echo "  up_elk         Build and start only the ELK stack services"
	@echo "  down           Stop and remove containers, networks, and volumes"
	@echo "  clean_volumes  Remove volumes and reset persistent data"
	@echo "  clean_orphans  Remove orphaned containers not defined in the current docker-compose.yml"
	@echo "  clean_images   Remove all Docker images"
	@echo "  clean_all      Full cleanup: containers, networks, volumes, and images"
	@echo "  clean          Default clean: reset data and ensure only defined services are running"
	@echo "  re             Rebuild and start all services with a clean environment"
	@echo "  logs_nginx     Tail logs from the Nginx service"
	@echo "  logs_backend   Tail logs from the Backend service"
	@echo "  logs_db        Tail logs from the Database service"
	@echo "  logs_elk       Tail logs from the ELK stack services"
	@echo "  status         Check status of running containers"
	@echo "  exec_nginx     Open a shell in the Nginx container"
	@echo "  exec_backend   Open a shell in the Backend container"
	@echo "  exec_db        Open a shell in the Database container"
	@echo "  exec_elk       Open a shell in the ELK stack container"
	@echo "  stop_all       Stop all running services without removing them"
	@echo "  help           Show this help message"

