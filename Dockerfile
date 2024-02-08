# Base image with Python and Java (needed for PySpark)
FROM python:3.12-slim as base

# Install Packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip ffmpeg curl espeak && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user with a home directory (necessary for whisper)
RUN groupadd -r chronos && useradd -r -g chronos -m -d /home/chronos chronos

# Create necessary directories
RUN mkdir /app && \
    mkdir -p /app/app/templates && \
    mkdir -p /app/app/static && \
    mkdir -p /app/app/models

WORKDIR /app

COPY requirements.txt .env run.py entrypoint.sh ./
COPY app/*.py ./app/
COPY app/templates ./app/templates
COPY app/static ./app/static

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Give execution rights to the entrypoint script and ensure it's owned by chronos
RUN chmod +x /app/entrypoint.sh && \
    chown -R chronos:chronos /app

# Switch to non-root user
USER chronos

EXPOSE 5000

# Set the script as the entry point
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
