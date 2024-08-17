#!/bin/sh

# Modify the database so it can store the data associated with any new models we’ve defined.
python manage.py makemigrations beePong
# Apply the migration (if any) and have Django modify the database for us accordingly.
python manage.py migrate


#python manage.py makemigrations beePong --noinput
# Apply the migration (if any) and have Django modify the database for us accordingly.
#python manage.py migrate --noinput

# Set the command to start the Django development server
exec python manage.py runserver 0.0.0.0:8000

