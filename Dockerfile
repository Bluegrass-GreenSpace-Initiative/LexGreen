FROM python:3.11-slim

# Prevents Python from writing .pyc files and buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# System deps (optional minimal)
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY . /app

# Ensure instance dir exists (will be backed by Fly volume at runtime)
RUN mkdir -p /app/instance /app/instance/uploads

EXPOSE 8080

# Use Gunicorn to serve Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers", "2", "--threads", "4"]

