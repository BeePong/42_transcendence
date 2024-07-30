FROM python:3.11-slim-buster

WORKDIR /beePong

# Install necessary utilities
RUN apt-get update && apt-get install -y curl procps

# Copy the requirements.txt file and install the Python dependencies
COPY requirements.txt /beePong/

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /beePong/

# Expose the port the Django application will run on
EXPOSE 8000

# Set the command to start the Django development server
RUN chmod +x /beePong/init_beePong.sh
ENTRYPOINT ["/beePong/init_beePong.sh"]

ENV PYTHONUNBUFFERED=1
