# Base image with Python and Java (needed for PySpark)
FROM openjdk:8-jdk-slim as base

# Install Packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip ffmpeg

RUN mkdir /app

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/ ./app

COPY run.py ./

EXPOSE 5000

CMD ["python3", "./run.py"]
