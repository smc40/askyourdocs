# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY req_freeze.txt req_freeze.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r req_freeze.txt

# Install Java needed for TIKA
RUN apt-get update && apt-get install -y default-jre && rm -rf /var/lib/apt/lists/*

# Copy the backend source code into the container at /app/backend
COPY app/backend app/backend/
COPY askyourdocs askyourdocs/
COPY docs docs/
COPY models models/
COPY resources resources/
RUN mkdir -p app/backend/uploads

# Run migrations
COPY db_migration.sh db_migration.sh
COPY entrypoint.sh entrypoint.sh
RUN chmod 777 db_migration.sh
RUN chmod 777 entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Run uvicorn when the container launches
CMD ./entrypoint.sh