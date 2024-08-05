# Mesop App Maker

Editor to generate, edit, and view Mesop apps using LLMs.

## Running the application

The Mesop App Maker consists of two Mesop apps, the editor and the code runner.

### The runner

The code runner is run using Docker to avoid potentially destructive code changes.

It can be started using these commands:

```shell
cd runner
pip install -r requirements.txt  # First time only
docker stop mesop-app;
docker rm mesop-app;
docker build -t mesop-app . && docker run --name mesop-app -d -p 8080:8080 mesop-app;
```

### The editor

The editor is the Mesop app that allows you to generate, edit, and view Mesop apps.

```
cd editor
pip install -r requirements.txt  # First time only
mesop main.py
```

You will need a Gemini API key to use the Mesop app generate functionality.
