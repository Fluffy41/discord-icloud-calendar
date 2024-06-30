# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy .env file into the container
COPY .env /app/.env

# Expose the port your app runs on
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]
