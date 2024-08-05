import constants as c
import mesop as me


@me.stateclass
class State:
  # App level
  loading: bool = False
  error: str
  info: str

  # Settings
  api_key: str
  model: str = "gemini-1.5-flash"
  url: str = c.DEFAULT_URL

  # Generate prompt panel
  prompt_mode: str = "Generate"
  prompt_placeholder: str
  prompt: str

  # Code editor
  code_placeholder: str = c.EXAMPLE_PROGRAM
  code: str = c.EXAMPLE_PROGRAM

  # App preview
  run_result: str
  url_path: str = "/"
  loaded_url: str
  iframe_index: int

  # Sidebar
  menu_open: bool = True
  menu_open_type: str = "settings"

  # Sub-screens
  show_error_dialog: bool = False
  show_generate_panel: bool = False
  show_status_snackbar: bool = False
