# Use the latest official Python image from the Docker Hub
FROM python:3.12.0-alpine3.18

# Set the working directory
WORKDIR /app

# Copy the website files to the working directory
COPY website /app/website

# Expose the port the server will run on
EXPOSE 8989

# Command to run the Python HTTP server
CMD ["python3", "-m", "http.server", "8989", "--directory", "/app/website"]

