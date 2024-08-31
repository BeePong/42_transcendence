#!/bin/bash

# Define the container name
CONTAINER_NAME="backendummy"

# Define the path to the script inside the container
SCRIPT_PATH="/beePong/tournament/ai.py"

# Execute the script inside the container
docker exec -it $CONTAINER_NAME python $SCRIPT_PATH > output.txt 2>&1