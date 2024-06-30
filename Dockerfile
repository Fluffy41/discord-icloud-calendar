# Use an appropriate Python base image for ARM
FROM arm32v7/python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Command to run your application
CMD ["python", "main.py"]
