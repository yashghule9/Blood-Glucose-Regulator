# Dockerfile for the Flask dashboard
FROM python:3.11-slim

# Install some packages required to install SciPy and NumPy wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gfortran \
      libatlas-base-dev \
      libopenblas-dev \
      liblapack-dev \
      && rm -rf /var/lib/apt/lists/*

# Create and use app directory
WORKDIR /app

# Install pip dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY . /app

# Set environment variables
ENV FLASK_APP=ap_dashboard.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# If you want gunicorn for production
EXPOSE 5000

# Use gunicorn as the startup command
CMD ["gunicorn", "-b", "0.0.0.0:5000", "ap_dashboard.app:app", "--workers", "4"]
