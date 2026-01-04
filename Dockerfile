FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g., if we decide to use other audio libs later)
# For now, minimal is fine.
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the Flask port
EXPOSE 5000

# Create a volume for downloads
VOLUME /downloads
ENV DOWNLOAD_DIR=/downloads

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
