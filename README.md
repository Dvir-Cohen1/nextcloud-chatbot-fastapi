# FastAPI Chatbot Service

## Overview

This repository contains a FastAPI service that acts as a chatbot for integration with Nextcloud. The service listens for webhook events from Nextcloud and processes them accordingly. The setup involves running the FastAPI application locally and connecting it to Nextcloud, which runs in a Docker container.

## Features

- **Webhook Integration**: Listens for and processes incoming webhook requests from Nextcloud.
- **FastAPI Framework**: Utilizes FastAPI for creating the web service.

## Prerequisites

1. **Python 3.8+**: Ensure you have Python 3.8 or newer installed.
2. **FastAPI**: Install FastAPI and `uvicorn` for running the app.
3. **Nextcloud**: Running in a Docker container.
4. **Docker** (for Nextcloud): Ensure Docker is installed if using Docker for Nextcloud.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### requirements.txt should include:
```plaintext
fastapi
uvicorn
httpx
```

### 4. Run the FastAPI Application
```bash
uvicorn main:app --reload
```
This command starts the FastAPI server locally at http://127.0.0.1:8000/.

## Connecting to Nextcloud
Ensure your Nextcloud instance is running on http://localhost:8080. The FastAPI service should be reachable from this address.

### 1. Install the Bot in Nextcloud
Use the following command to install and configure the bot:
```bash
php /var/www/html/occ talk:bot:install --feature webhook <NAME> <BOT_SECRET> <BOT_WEBHOOK_URL> <DESCRIPTION>
```

Replace <> with your actual details.

### 2. Verify Webhook Communication
Send a test message from Nextcloud and ensure that your FastAPI service logs or processes the message as expected. If communication fails, ensure that Nextcloud can reach http://127.0.0.1:8000.

## Commands
- Run the FastAPI Application: uvicorn main:app --reload
- Install Python Dependencies: pip install -r requirements.txt
- Activate Virtual Environment: source venv/bin/activate (Windows: venv\Scripts\activate)

## Troubleshooting
- Connection Issues: If you receive errors like Failed to connect, ensure that the FastAPI service is running and accessible from the Nextcloud Docker container. You may need to adjust Docker networking settings or use the IP address of the host machine instead of localhost.
- Dependency Errors: Make sure all dependencies are installed and correctly listed in requirements.txt.

## Acknowledgements
- FastAPI
- Nextcloud