# Use Python slim image as base to minimize container size
FROM python:3.11-slim

# Set the working directory for all subsequent commands
WORKDIR /app

# Copy all files from build context to container
COPY . /app

# Create necessary directories for data processing and output storage
RUN mkdir -p /app/data /app/output

# Install Python dependencies from requirements.txt
# --no-cache-dir reduces image size by not caching pip packages
RUN pip install --no-cache-dir -r requirements.txt

# Configure NLTK data path and download required wordnet dataset
# This ensures natural language processing capabilities are available
ENV NLTK_DATA=/usr/local/nltk_data
RUN python -m nltk.downloader -d /usr/local/nltk_data wordnet

# Grant execution permissions to the entrypoint script
# This ensures the script can be executed when container starts
RUN chmod +x /app/entrypoint.sh

# Set the container's entrypoint script
# This script will be executed when the container starts
ENTRYPOINT ["/app/entrypoint.sh"]