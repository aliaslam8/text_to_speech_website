FROM python:3.11-slim

# Install FFmpeg and other system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 3000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=3000

# Run the application
CMD ["python", "src/main.py"]

