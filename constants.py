DEFAULT_URL = "http://localhost:8080"
EXAMPLE_PROGRAM = """
import mesop as me

@me.page()
def app():
  me.text("Hello World")
""".strip()
PROMPT_MODE_GENERATE = "Generate"
PROMPT_MODE_REVISE = "Revise"

HELP_TEXT = """
**Generating Mesop Apps**

- Provide a Gemini API Key in the Settings panel.
- Click the lightning bolt button to open the prompt panel.
- Enter your prompt and generate your app.
- Inspect the generated code in the editor.
- Press the run/play button to execute and view your code
    - *Requires Mesop App Runner instance.*

**Setting up a Mesop Runner instance**

*If running on Hugging Face, you will need to fork the Mesop App Runner space.*

- Start up an instance of the [Mesop App Runner](https://github.com/richard-to/mesop-app-runner).
    - See [Github repository](https://github.com/richard-to/mesop-app-runner) for more details.
- Provide the Runner URL to your instance.
- Provide the Runner Token to your runner instance.
""".strip()
