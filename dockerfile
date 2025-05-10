# Use an official Python image
FROM python:3.13.3

# Install system dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates fonts-liberation libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libappindicator1 libasound2 xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && chmod +x /usr/local/bin/chromedriver

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH=$PATH:/usr/local/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt

# Expose the port
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
