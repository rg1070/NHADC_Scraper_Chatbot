# Use an official Python image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install system dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget unzip gnupg ca-certificates \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${CHROME_BIN}:${PATH}"

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt

# Expose port
EXPOSE 8000

# Run FastAPI app from backend.main
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
