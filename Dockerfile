# Start with a Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /workspace

# Copy the requirements file
COPY requirements.txt /workspace/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code into the container
COPY . /workspace
