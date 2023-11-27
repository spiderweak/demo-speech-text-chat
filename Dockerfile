# Base image with Python and Java (needed for PySpark)
FROM openjdk:8-jdk-slim as base

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl vim

RUN mkdir /app
# Set the working directory
WORKDIR /app

# Copy only the requirements file, to cache the installed dependencies
COPY requirements.txt ./

COPY app/static /app/static

COPY app/templates /app/templates

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the application
CMD ["python3", "./run.py"]

