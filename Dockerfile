FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz \
    && tar -xvzf geckodriver-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]