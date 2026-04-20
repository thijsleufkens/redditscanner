# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/reddit_posts.db

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the scanner code
COPY scanner/ ./scanner/

# Set working directory to scanner for easier execution
WORKDIR /app/scanner

# Default command
CMD ["python", "main.py"]
