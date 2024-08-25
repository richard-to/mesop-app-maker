import os

import mesop as me

import constants as c


@me.stateclass
class State:
  # App level
  loading: bool = False
  error: str
  info: str

  # Settings
  api_key: str = os.getenv("GEMINI_API_KEY", "")
  model: str = "gemini-1.5-flash"
  runner_url: str = os.getenv("MESOP_APP_MAKER_RUNNER_URL", c.DEFAULT_URL)
  runner_token: str = os.getenv("MESOP_APP_MAKER_RUNNER_TOKEN", "")

  # Generate prompt panel
  prompt_mode: str = "Generate"
  prompt_app_type: str = "general"
  prompt_placeholder: str
  prompt: str

  # New template dialog
  select_index: int

  # Prompt history panel
  prompt_history: list[dict]  # Format: {"prompt", "code", "index", "mode", "app_type"}

  # Code editor
  code_placeholder: str = c.EXAMPLE_PROGRAM
  code: str = c.EXAMPLE_PROGRAM

  # App preview
  run_result: str
  runner_url_path: str = "/"
  loaded_url: str
  iframe_index: int

  # Sidebar
  menu_open: bool = True
  menu_open_type: str = "settings"

  # Sub-screens
  show_error_dialog: bool = False
  show_generate_panel: bool = False
  show_prompt_history_panel: bool = False
  show_status_snackbar: bool = False
  show_help_dialog: bool = bool(int(os.getenv("MESOP_APP_MAKER_SHOW_HELP", "0")))
  show_new_dialog: bool = False

  # Async action
  async_action_name: str
  async_action_duration: int = 3
