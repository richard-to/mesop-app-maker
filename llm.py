import google.generativeai as genai


with open("prompt.txt") as f:
  SYSTEM_INSTRUCTION = f.read()


GENERATE_APP_BASE_PROMPT = """
Your task is to write a Mesop app.

Instructions:
1. For the @me.page decorator, leave it empty like this `@me.page()`
2. Event handler functions cannot use lambdas. You must use functions.
3. Event handle functions only pass in the event type. They do not accept extra parameters.
4. For padding, make sure to use the the `me.Padding` object rather than a string or int.
5. For margin, make sure to use the the `me.Margin` object rather than a string or int.
6. For border, make sure to use the the `me.Border` and `me.BorderSide` objects rather than a string.
7. For buttons, prefer using type="flat", especially if it is the primary button.
8. Only output the python code.

Here is a description of the app I want you to write:

<APP_DESCRIPTION>

""".strip()

REVISE_APP_BASE_PROMPT = """
Your task is to modify a Mesop app given the code and a description.

Make sure to remember these rules when making modifications:
1. For the @me.page decorator, leave it empty like this `@me.page()`
2. Event handler functions cannot use lambdas. You must use functions.
3. Event handle functions only pass in the event type. They do not accept extra parameters.
4. For padding, make sure to use the the `me.Padding` object rather than a string or int.
5. For margin, make sure to use the the `me.Margin` object rather than a string or int.
6. For border, make sure to use the the `me.Border` and `me.BorderSide` objects rather than a string.
7. For buttons, prefer using type="flat", especially if it is the primary button.
8. Only output the python code.

Here is is the code for the app:

```
<APP_CODE>
```

Here is a description of the changes I want:

<APP_CHANGES>

""".strip()


def make_model(api_key: str, model_name: str) -> genai.GenerativeModel:
  genai.configure(api_key=api_key)

  generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 32768,
  }

  safety_settings = [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_NONE",
    },
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_NONE",
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_NONE",
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_NONE",
    },
  ]

  return genai.GenerativeModel(
    model_name=model_name,
    system_instruction=SYSTEM_INSTRUCTION,
    safety_settings=safety_settings,
    generation_config=generation_config,
  )


def generate_mesop_app(msg: str, model_name: str, api_key: str) -> str:
  model = make_model(api_key, model_name)
  response = model.generate_content(
    GENERATE_APP_BASE_PROMPT.replace("<APP_DESCRIPTION>", msg), request_options={"timeout": 120}
  )
  return response.text


def adjust_mesop_app(code: str, msg: str, model_name: str, api_key: str) -> str:
  model = make_model(api_key, model_name)
  response = model.generate_content(
    REVISE_APP_BASE_PROMPT.replace("<APP_CODE>", code).replace("<APP_CHANGES>", msg),
    request_options={"timeout": 120},
  )
  return response.text
