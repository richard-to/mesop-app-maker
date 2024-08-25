---
title: Mesop App Maker
emoji: 🏭
colorFrom: yellow
colorTo: pink
sdk: docker
pinned: false
license: apache-2.0
app_port: 8080
---

# Mesop App Maker

Editor to generate, edit, and view Mesop apps using LLMs.

## Usage

The Mesop App Maker consists of two Mesop apps, the editor and the app runner.

### The editor

The editor is the Mesop app that allows you to generate, edit, and view Mesop apps.

```shell
pip install -r requirements.txt
mesop main.py
```

#### Environment variables

The editor supports the following environment variables. These are mainly useful for
local development where you don't want to keep entering your API Key and runner token
after every reload.

```
GEMINI_API_KEY=you-gemini-api-key
MESOP_APP_MAKER_RUNNER_URL=https://example.com
MESOP_APP_MAKER_RUNNER_TOKEN=your-secret-token
MESOP_APP_MAKER_SHOW_HELP=0
```

You will need a Gemini API key to use the Mesop app generate functionality.

### The runner

> The runner has been moved to https://github.com/richard-to/mesop-app-runner.

The [Mesop App Runner](https://github.com/richard-to/mesop-app-runner) uses Docker to avoid potentially destructive code changes.

It can be started using these commands:

```shell
# In mesop-app-runner directory
docker stop mesop-app-runner;
docker rm mesop-app;
docker build -t mesop-app-runner . && docker run --name mesop-app-runner \
  -e MESOP_APP_RUNNER_TOKEN=your-secret-token \
  -d -p 8080:8080 mesop-app-runner;
```

## Screenshots

### Generate app

<img width="1312" alt="Screenshot 2024-08-05 at 5 29 44 PM" src="https://github.com/user-attachments/assets/d96afd8a-3c09-4d12-8749-00deddc7f8f5">

### Preview app

<img width="1312" alt="Screenshot 2024-08-05 at 5 31 35 PM" src="https://github.com/user-attachments/assets/1a826d44-c87b-4c79-aeaf-29bc8da3b1c0">
