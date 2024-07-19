.PHONY: build up 

# Create directories for mounting volumes

all: build up

# Build the Docker images
build: 
	docker compose -f ./docker-compose.yml build

# Start the services
up: build	
	docker compose -f ./docker-compose.yml up -d

# Stop the services
clean:
	docker rm -vf $$(docker ps -aq)
	docker rmi -f $$(docker images -aq)

re: clean all
