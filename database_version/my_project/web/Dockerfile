# Use the official Python image from the Docker Hub
FROM python:3.9

# Set environment variable to ensure output is sent straight to terminal (not buffered)
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container at /code/
COPY requirements.txt /code/

# Install any dependencies
RUN pip install -r requirements.txt

# Download and set permissions for wait-for-it.sh
RUN apt-get update && apt-get install -y curl \
    && curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x wait-for-it.sh

# Copy the current directory contents into the container at /code/
COPY . /code/


