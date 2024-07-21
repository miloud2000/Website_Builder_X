# Use an official Python runtime as a parent image
FROM python:3.10.11-slim-buster

# Set the working directory to /app
WORKDIR /app
# Install postgresql-dev package
# RUN apt-get update && \ 
#     apt-get install -y gcc postgresql-client postgresql-contrib libpq-dev && \
#     rm -rf /var/lib/apt/lists/*
COPY . .
# Set $PATH environment variable
# ENV PATH=$PATH:/usr/lib/postgresql/12/bin/
# Copy the poetry.lock and pyproject.toml files to the container
# COPY poetry.lock pyproject.toml ./
# RUN pip install psycopg2-binary 
# Install poetry and project dependencies
RUN  pip install django
RUN  apt install npm
RUN  pip install django-chartjs
RUN  npm install chart.js
RUN  pip install xhtml2pdf 


# RUN poetry config virtualenvs.create false 
# RUN poetry install --no-interaction --no-ansi 
# Copy the rest of the project files to the container

# RUN rm -rf ./SwPreprocessingApp/migrations/*

# Expose port 8080 (replace with the port your app listens on)
EXPOSE 8000

# Run the Django commands on container startup
CMD  python manage.py runserver 54.37.65.172:8000