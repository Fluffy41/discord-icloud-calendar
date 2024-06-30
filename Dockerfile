# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install build essentials including GCC
RUN apt-get update && apt-get install -y gcc

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your main.py script into the container at /app
COPY main.py /app/

# Run main.py when the container launches
CMD ["python", "main.py"]
