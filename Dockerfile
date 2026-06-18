FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install curl for supercronic download
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install supercronic (Go-based cron daemon for containers)
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.29/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=cd48d45c4b10f3f0bfdd3a57d054cd05ac96812b

RUN curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM} ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/supercronic"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only to keep image lean)
RUN playwright install chromium --with-deps

COPY pat_rotator.py .

# /data is the volume mount for persisting browser state
VOLUME ["/data"]

# Default: run once and exit. Use cron/supercronic outside for scheduling.
CMD ["python", "pat_rotator.py"]
