# Base image with Python and Java (needed for PySpark)
FROM openjdk:8-jdk-slim as base

# Install Packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip ffmpeg curl

RUN mkdir /app

WORKDIR /app

COPY requirements.txt ./

RUN mkdir -p ./app/templates
RUN mkdir -p ./app/static
RUN mkdir -p ./app/models

COPY app/*.py ./app/
COPY app/templates ./app/templates
COPY app/static ./app/static

COPY .env ./
COPY run.py ./

RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh

# Give execution rights to the entrypoint script
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

# Set the script as the entry point
ENTRYPOINT ["/app/entrypoint.sh"]

# Set the command to run the application
CMD ["python3", "./run.py"]
