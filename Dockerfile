# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# Ensure production servers are installed
RUN pip install gunicorn uvicorn

# Copy the project code into the container
COPY . /app/

# Collect static files (for Swagger UI, admin, etc.)
RUN python manage.py collectstatic --noinput --clear || true

# Expose port 8000 for the application
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "supercareer.wsgi:application"]
