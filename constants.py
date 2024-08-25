DEFAULT_URL = "http://localhost:8080"
EXAMPLE_PROGRAM = """
import mesop as me

@me.page()
def app():
  me.text("Hello World")
""".strip()
PROMPT_MODE_GENERATE = "Generate"
PROMPT_MODE_REVISE = "Revise"
