.PHONY: build up backend

# Create directories for mounting volumes

all: build up

# Build the Docker images
build: 
	docker compose -f docker-compose.yml build

# Start the services
up: build	
	docker compose -f docker-compose.yml up -d

# Rebuild and restart the backend service
backend:
	docker compose -f docker-compose.yml build backend_dummy
	docker compose -f docker-compose.yml up -d backend_dummy

# Stop the services
clean:
	docker rm -vf $$(docker ps -aq)
	docker rmi -f $$(docker images -aq)

re: clean all