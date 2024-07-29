import google.generativeai as genai

REPAIR_PROMPT = ""


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
    model_name=model_name, safety_settings=safety_settings, generation_config=generation_config
  )


def build_mesop_app(msg: str, model_name: str, api_key: str) -> str:
  model = make_model(api_key, model_name)
  response = model.generate_content(
    "Generate a Mesop app.\n\n" + msg, request_options={"timeout": 120}
  )
  return response.text


def adjust_mesop_app(code: str, msg: str, model_name: str, api_key: str) -> str:
  model = make_model(api_key, model_name)
  response = model.generate_content(
    "Can you update the following code? " + msg + "\n\n" + code, request_options={"timeout": 120}
  )
  return response.text
