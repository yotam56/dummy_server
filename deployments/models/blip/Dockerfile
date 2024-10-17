# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the deployments directory and its subdirectories
COPY deployments/ /app/deployments/

# Copy the requirements files into the container
COPY deployments/base_requirements.txt /app/
COPY deployments/models/blip/requirements.txt /app/

# Install base requirements first
RUN pip install --no-cache-dir -r /app/base_requirements.txt

# Install the second requirements file, overriding the previous versions if necessary
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run FastAPI using Uvicorn
CMD ["uvicorn", "deployments.models.blip.main:app", "--host", "0.0.0.0", "--port", "8000"]
