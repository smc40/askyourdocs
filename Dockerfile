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
RUN /bin/bash -c 'source ./app/backend/.env'

# Expose the port the app runs on
EXPOSE 8000

# Run uvicorn when the container launches
CMD ["uvicorn", "app.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]