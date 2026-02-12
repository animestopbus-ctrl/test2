FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# Create logs directory with proper permissions
RUN mkdir -p logs && chmod 755 logs

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make Python script executable
RUN chmod +x app.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python health_check.py || exit 1

# Run the bot with error handling
CMD ["sh", "-c", "python app.py 2>&1 | tee logs/bot.log"]
