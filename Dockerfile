# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install required system packages, including dnsutils for DNS resolution
RUN apt-get update && apt-get install -y curl gnupg dnsutils

# Copy the requirements.txt into the container
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . /app

# Expose Streamlit's default port
EXPOSE 8501

# Run the application with hot-reloading enabled
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]
