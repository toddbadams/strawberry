# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /src

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy your loader and any other code files
COPY loader.py ./
COPY src/ ./src/    

# Expose ports or volumes here if needed
# VOLUME ["/usr/src/app/data"]

# Default command: run loader.py
CMD ["python", "loader.py"]
