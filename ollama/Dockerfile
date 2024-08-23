# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Install essential build tools, git, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install a compatible version of numpy
RUN pip install numpy==2.0.1

# Install torch separately before flash-attn
RUN pip install torch==2.1.2

# Install decord from GitHub
RUN pip install git+https://github.com/dmlc/decord.git

# Install flash-attn separately to ensure it's available
RUN pip install flash-attn==2.6.2

# Copy the requirements file into the container
COPY requirements.txt .

# Install remaining dependencies (excluding torch, numpy, and flash-attn)
RUN sed -i '/torch/d;/numpy/d;/flash-attn/d' requirements.txt && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Copy the video file into the container
COPY test_video.mov /app/video_test.mov

# Define the command to run your application
CMD ["python", "run_model.py"]
