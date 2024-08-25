from typing import Tuple

import google.generativeai as genai


with open("prompt/base_system_instructions.txt") as f:
  SYSTEM_INSTRUCTION = f.read()


with open("prompt/base_examples.txt") as f:
  DEFAULT_EXAMPLES = f.read()


with open("prompt/chat_elements_examples.txt") as f:
  CHAT_ELEMENTS_EXAMPLES = f.read()


with open("prompt/chat_examples.txt") as f:
  CHAT_EXAMPLES = f.read()


GENERATE_APP_BASE_PROMPT = """
Your task is to write a Mesop app.

Instructions:
1. For the @me.page decorator, leave it empty like this `@me.page()`
2. Event handler functions cannot use lambdas. You must use functions.
3. Event handler functions only pass in the event type. They do not accept extra parameters.
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
3. Event handler functions only pass in the event type. They do not accept extra parameters.
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


GENERATE_CHAT_APP_BASE_PROMPT = """
Your task is to write a Mesop chat app.

Instructions:
1. For the @me.page decorator, leave it empty like this `@me.page()`
2. Event handler functions cannot use lambdas. You must use functions.
3. Event handler functions only pass in the event type. They do not accept extra parameters.
4. For padding, make sure to use the the `me.Padding` object rather than a string or int.
5. For margin, make sure to use the the `me.Margin` object rather than a string or int.
6. For border, make sure to use the the `me.Border` and `me.BorderSide` objects rather than a string.
7. For buttons, prefer using type="flat", especially if it is the primary button.
8. Remember that me.box is a like a div. So you can use similar CSS styles for layout.
9. Only output the python code.

Here is a description of the chat app I want you to write:

<APP_DESCRIPTION>

""".strip()

REVISE_CHAT_APP_BASE_PROMPT = """
Your task is to modify a Mesop chat app given the code and a description.

Make sure to remember these rules when making modifications:
1. For the @me.page decorator, leave it empty like this `@me.page()`
2. Event handler functions cannot use lambdas. You must use functions.
3. Event handler functions only pass in the event type. They do not accept extra parameters.
4. For padding, make sure to use the the `me.Padding` object rather than a string or int.
5. For margin, make sure to use the the `me.Margin` object rather than a string or int.
6. For border, make sure to use the the `me.Border` and `me.BorderSide` objects rather than a string.
7. For buttons, prefer using type="flat", especially if it is the primary button.
8. Remember that me.box is a like a div. So you can use similar CSS styles for layout.
9. Only output the python code.

Here is is the code for the chat app:

```
<APP_CODE>
```

Here is a description of the changes I want:

<APP_CHANGES>

""".strip()


def make_model(
  api_key: str, model_name: str, additional_instructions: str
) -> genai.GenerativeModel:
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
    system_instruction=SYSTEM_INSTRUCTION + additional_instructions,
    safety_settings=safety_settings,
    generation_config=generation_config,
  )


def get_prompt_examples(app_type: str) -> str:
  if app_type == "chat":
    return CHAT_ELEMENTS_EXAMPLES + CHAT_EXAMPLES
  return DEFAULT_EXAMPLES


def get_generate_prompt_base(app_type: str) -> str:
  if app_type == "chat":
    return GENERATE_CHAT_APP_BASE_PROMPT
  return GENERATE_APP_BASE_PROMPT


def get_revise_prompt_base(app_type: str) -> str:
  if app_type == "chat":
    return REVISE_CHAT_APP_BASE_PROMPT
  return REVISE_APP_BASE_PROMPT


def generate_mesop_app(msg: str, model_name: str, api_key: str, app_type: str) -> str:
  model = make_model(api_key, model_name, get_prompt_examples(app_type))
  response = model.generate_content(
    get_generate_prompt_base(app_type).replace("<APP_DESCRIPTION>", msg),
    request_options={"timeout": 120},
  )
  return response.text


def adjust_mesop_app(code: str, msg: str, model_name: str, api_key: str, app_type: str) -> str:
  model = make_model(api_key, model_name, get_prompt_examples(app_type))
  response = model.generate_content(
    get_revise_prompt_base(app_type).replace("<APP_CODE>", code).replace("<APP_CHANGES>", msg),
    request_options={"timeout": 120},
  )
  return response.text
