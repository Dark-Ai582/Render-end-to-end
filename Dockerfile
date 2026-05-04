FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# ✅ FIXED VERSION
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz \
    && tar -xvzf geckodriver-v0.34.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]