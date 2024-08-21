.PHONY: up down clean clean_volumes clean_orphans clean_images clean_all get_images_id re re_elk re_all re_all_elk  up_backend up_db up_elk up_all up_no_elk logs logs_errors logs_grep logs_nginx logs_backend logs_db logs_elk ps ps_short ps_inspect exec_nginx exec_backend exec_db exec_elk stop_all stats sys_df help nuke

################################################################################
# Build and Start
################################################################################
# Default target: Build and start all services except ELK stack
all: up_no_elk

# Start all services except ELK stack and rebuild if necessary
up_no_elk:
	docker compose -f ./docker-compose.yml up --build -d nginx backend_dummy db pgadmin

# Start all services including ELK stack and rebuild if necessary
up_all:
	docker compose -f ./docker-compose.yml up --build -d

up_backend:
	docker compose -f ./docker-compose.yml up --build -d backend_dummy

up_db:
	docker compose -f ./docker-compose.yml up --build -d db

up_elk:
	docker compose -f ./docker-compose.yml up --build -d elasticsearch kibana logstash metricbeat

################################################################################
# Clean and Remove
################################################################################
# Capture image IDs to .image_ids before bringing containers down
get_images_id:
	@images=$$(docker compose -f ./docker-compose.yml images -q); \
	if [ -n "$$images" ]; then \
		echo "$$images" >> .image_ids; \
	else \
		echo "get_images_id: no images to be deleted"; \
	fi; \
	sort .image_ids | uniq > .image_ids.tmp && mv .image_ids.tmp .image_ids; \
	echo "get_images_id: images to be deleted identified"; \
	cat .image_ids

# Stop and remove containers, networks, and volumes
down: get_images_id
	docker compose -f ./docker-compose.yml down

# Clean up volumes and reset persistent data
clean_volumes: get_images_id
	docker compose -f ./docker-compose.yml down -v

# Clean up orphans to remove containers that are no longer defined in the current docker-compose.yml
clean_orphans: get_images_id
	docker compose -f ./docker-compose.yml down --remove-orphans

# Clean up images present in .image_ids, delete the file, and remove all Docker images
clean_images:
	@if [ -f .image_ids ]; then \
		echo "clean_images: remove following images"; \
		cat .image_ids; \
		images=$$(cat .image_ids); \
		if [ -n "$$images" ]; then \
			for image in $$images; do \
				docker image rm -f $$image || true; \
			done; \
			echo "clean_images: Images removed"; \
		else \
			echo "clean_images: No images to remove"; \
		fi; \
		rm -f .image_ids; \
	else \
		echo "clean_images: .image_ids file not found"; \
	fi

# Clean up all: containers, networks, volumes, and images
# Use this for a full cleanup of the Docker environment
clean_all: clean_orphans clean_volumes clean_images 

# Clean up: containers, networks, volumes, and orphans (default clean)
# Use this to reset data and ensure only defined services are running
clean: clean_orphans clean_volumes

################################################################################
# Rebuild and Restart
################################################################################
# Rebuild and start all services without removing volumes
re: clean_orphans clean_images up_no_elk

# Rebuild and start all services including ELK stack without removing volumes
re_elk: clean_orphans clean_images up_all

# Rebuild and start all services with a full cleanup including volumes
re_all: clean_all up_no_elk

# Rebuild and start all services including ELK stack with a full cleanup including volumes
re_all_elk: clean_all up_all

################################################################################
# Logging
################################################################################
# Tail logs from specific services
logs_nginx:
	docker compose -f ./docker-compose.yml logs -f nginx

logs_backend:
	docker compose -f ./docker-compose.yml logs -f backend_dummy

logs_db:
	docker compose -f ./docker-compose.yml logs -f db

logs_elk:
	docker compose -f ./docker-compose.yml logs -f elasticsearch kibana logstash metricbeat dashboard_import

# Tail all logs with timestamps
logs:
	docker compose -f ./docker-compose.yml logs -f -t

# Tail ERROR logs with timestamps
logs_errors:
	docker compose -f ./docker-compose.yml logs -f -t | grep "ERROR"

# Tail logs containing keyword input by user with timestamps
logs_grep:
	@read -p "Enter keyword to search in logs: " keyword; docker compose -f ./docker-compose.yml logs -f -t | grep "$$keyword"

################################################################################
# Status
################################################################################
# Check status of running containers
ps:
	docker compose -f ./docker-compose.yml ps

# Check status of running containers with concise output
ps_short:
	@docker container ls -a --format "table {{.ID}}\t{{.Names}}\t{{.RunningFor}}\t{{.Status}}"

# Inspect a specific container
ps_inspect: ps_short
	@echo ""
	@read -p "Enter container name: " name; docker inspect $$name

################################################################################
# Exec into Containers
################################################################################
# Open a shell in a specific container
exec_nginx:
	docker compose -f ./docker-compose.yml exec nginx sh

exec_backend:
	docker compose -f ./docker-compose.yml exec backend_dummy sh

exec_db:
	docker compose -f ./docker-compose.yml exec db sh

exec_elk:
	docker compose -f ./docker-compose.yml exec elasticsearch sh

################################################################################
# Stop services
################################################################################
# Stop all services without removing them
stop_all:
	docker compose -f ./docker-compose.yml stop

################################################################################
# Monitoring
################################################################################
stats:
	docker stats

sys_df:
	docker system df


################################################################################
# Reset repository to last commit (destructive action)
################################################################################
nuke:
	git clean -dxf
	git reset --hard	

################################################################################
# Help
################################################################################
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo ""
	@echo "Build and Start:"
	@echo "  all            Build and start all services except ELK stack"
	@echo "  up_all         Build and start all services including ELK stack"
	@echo "  up_backend     Build and start only the backend service"
	@echo "  up_db          Build and start only the database service"
	@echo "  up_elk         Build and start only the ELK stack services"
	@echo ""
	@echo "Stop:"
	@echo "  stop_all       Stop all running services without removing them"
	@echo ""
	@echo "Clean and Remove:"
	@echo "  down           Stop and remove containers, networks, and volumes"
	@echo "  clean_volumes  Remove volumes and reset persistent data"
	@echo "  clean_orphans  Remove orphaned containers not defined in the current docker-compose.yml"
	@echo "  clean_images   Remove all Docker images"
	@echo "  clean_all      Full cleanup: containers, networks, volumes, and images"
	@echo "  clean          Default clean: reset data and ensure only defined services are running"
	@echo ""
	@echo "Rebuild and Restart:"
	@echo "  re             Rebuild and start all services without removing volumes"
	@echo "  re_elk         Rebuild and start all services including ELK stack without removing volumes"
	@echo "  re_all         Rebuild and start all services with a full cleanup including volumes"
	@echo "  re_all_elk     Rebuild and start all services including ELK stack with a full cleanup including volumes"
	@echo ""
	@echo "Logging:"
	@echo "  logs_nginx     Tail logs from the Nginx service"
	@echo "  logs_backend   Tail logs from the Backend service"
	@echo "  logs_db        Tail logs from the Database service"
	@echo "  logs_elk       Tail logs from the ELK stack services"
	@echo "  logs           Tail all logs with timestamps"
	@echo "  logs_errors    Tail logs with timestamps and filter for ERROR messages"
	@echo "  logs_grep      Tail logs with timestamps and filter by a keyword"
	@echo ""
	@echo "Status:"
	@echo "  ps             Check status of running containers"
	@echo "  ps_short       Check status of running containers with concise output"
	@echo "  ps_inspect     Inspect a specific container"
	@echo ""
	@echo "Exec into Containers:"
	@echo "  exec_nginx     Open a shell in the Nginx container"
	@echo "  exec_backend   Open a shell in the Backend container"
	@echo "  exec_db        Open a shell in the Database container"
	@echo "  exec_elk       Open a shell in the ELK stack container"
	@echo ""
	@echo "Monitoring:"
	@echo "  stats          Show resource utilization statistics for running containers"
	@echo "  sys_df         Show Docker system disk usage"
	@echo ""
	@echo "Reset repository:"
	@echo "  nuke           Reset repository to the last commit (destructive action, removes all untracked files)"
	@echo ""
	@echo "Help:"
	@echo "  help           Show this help message"
