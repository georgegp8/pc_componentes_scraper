FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory for persistent volume
RUN mkdir -p /data

# Copy and make start script executable
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Run the application with Python script
CMD ["python", "run.py"]
