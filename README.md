# CSV Music Downloader

A simple Flask application to download music from a CSV list of FLAC URLs, tag them with metadata, and save them directly to a server directory. Designed for deployment on Coolify.

## Features
- Upload CSV with `FLAC URL`, `Artist`, `Title`, `Album`.
- Metadata tagging (Artist, Title, Album) using `mutagen`.
- Direct filestore download (no zip generation).
- Dockerized for easy VPS deployment.

## Prerequisites
- Python 3.9+ (for local dev)
- Docker
- A persistent directory for downloads (e.g., `/plex-media/music/`).

## Quick Start (Local)

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Application:**
    ```bash
    # Set download location (default is /downloads)
    export DOWNLOAD_DIR=./my_downloads
    python app.py
    ```

3.  **Access:** Open `http://localhost:5000`

## Docker Setup

1.  **Build:**
    ```bash
    docker build -t csv-downloader .
    ```

2.  **Run:**
    ```bash
    # Update /path/to/music to your actual local path
    docker run -p 5000:5000 \
      -v /path/to/music:/downloads \
      csv-downloader
    ```

## Coolify Deployment Guide

1.  **Create Service:**
    - Create a new **Docker** service in Coolify.
    - Provide the Dockerfile or link your Git repository.

2.  **Configure Ports:**
    - Expose port `5000`.

3.  **Configure Storage (Crucial):**
    - Go to **Storage**.
    - Add a new volume.
    - **Mount Path (Container):** `/downloads`
    - **Host Path (Server):** `/home/ubuntu/plex-media/music/[to be processed]/` (or your desired path).

4.  **Deploy:**
    - Click "Deploy". The app will be available at your configured domain.
