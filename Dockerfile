# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# The port that the application listens on. Cloud Run will set this environment variable.
ENV PORT 8080

# Expose the port
EXPOSE 8080

# Command to run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
