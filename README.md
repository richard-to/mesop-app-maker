# Mesop App Maker

Editor to generate, edit, and view Mesop apps using LLMs.

## Running the application

The Mesop App Maker consists of two Mesop apps, the editor and the code runner.

### The runner

The code runner is run using Docker to avoid potentially destructive code changes.

It can be started using these commands:

```shell
cd runner
docker stop mesop-app;
docker rm mesop-app;
docker build -t mesop-app . && docker run --name mesop-app -d -p 8080:8080 mesop-app;
```

### The editor

The editor is the Mesop app that allows you to generate, edit, and view Mesop apps.

```shell
cd editor
pip install -r requirements.txt  # First time only
mesop main.py
```

You will need a Gemini API key to use the Mesop app generate functionality.

## Screenshots

### Generate app

<img width="1312" alt="Screenshot 2024-08-05 at 5 29 44 PM" src="https://github.com/user-attachments/assets/d96afd8a-3c09-4d12-8749-00deddc7f8f5">

### Preview app

<img width="1312" alt="Screenshot 2024-08-05 at 5 31 35 PM" src="https://github.com/user-attachments/assets/1a826d44-c87b-4c79-aeaf-29bc8da3b1c0">
