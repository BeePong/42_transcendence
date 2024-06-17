FROM python

WORKDIR /beePong

# Copy the requirements.txt file and install the Python dependencies
COPY requirements.txt /beePong/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /beePong/

# Expose the port the Django application will run on
EXPOSE 8000

# Set the command to start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

ENV PYTHONUNBUFFERED=1