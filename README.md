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

### 4. Create and Set Environment Variables
```bash
# .env file

NEXTCLOUD_BOT_SECRET=
NEXTCLOUD_URL=http:
```

### 5. Run the FastAPI Application
```bash
# In Development
uvicorn main:app --host <IPv4 Address> --port 8000
```
This command starts the FastAPI server locally at http://<IPv4_Address>:8000/.

## Connecting to Nextcloud
Ensure the Nextcloud instance is running and reachable.
### 1. Install the Bot in Nextcloud
Use the following command to install and configure the bot:
```bash
# Replace <> with your actual details.

php /var/www/html/occ talk:bot:install --feature bots-v1 <BOT_NAME> <BOT_SECRET> <BOT_SERVICE_URL/webhook> <DESCRIPTION>
```
See full documntation here: [OCC documentation](https://nextcloud-talk.readthedocs.io/en/stable/occ/#talkbotinstall)


### 2. Verify Webhook Communication
Send a test message from Nextcloud and ensure that your FastAPI service logs or processes the message as expected. If communication fails, ensure that Nextcloud can reach the bot address.

### 3. Enable Bot in chat
- optional: Create new chat in Talk app and give it a name eg: Bot
- Enable bot in chat setting.
- send any message.

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