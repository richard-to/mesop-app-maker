import base64
import time

import requests
import mesop as me
import mesop.labs as mel
import components as mex
from web_components import code_mirror_editor_component

_COLOR_MENU_PANE = me.theme_var("surface-container")
_COLOR_MENU = me.theme_var("surface-container-low")
_COLOR_BG = me.theme_var("surface-container-lowest")
DEFAULT_URL = "http://localhost"
EXAMPLE_PROGRAM = """
import mesop as me

@me.page(title="Example App", security_policy=me.SecurityPolicy(allowed_iframe_parents=["localhost:*"]))
def app():
  me.text("Hello World")
""".strip()

llm = None


@me.stateclass
class State:
  code_placeholder: str = EXAMPLE_PROGRAM
  code: str = EXAMPLE_PROGRAM
  url: str = DEFAULT_URL
  loaded_url: str
  iframe_index: int
  run_result: str
  loading: bool = False
  prompt_placeholder: str
  prompt: str
  error: str
  info: str
  api_key: str
  model: str = "gemini-1.5-flash"
  menu_open: bool = True
  menu_open_type: str = "settings"
  revision_mode: bool = False


@me.page(
  title="Mesop AI Editor",
  stylesheets=[
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/theme/tomorrow-night-eighties.min.css",
  ],
  security_policy=me.SecurityPolicy(
    allowed_connect_srcs=[
      "https://cdnjs.cloudflare.com",
      "*.fonts.gstatic.com",
    ],
    allowed_script_srcs=["https://cdnjs.cloudflare.com", "*.fonts.gstatic.com"],
  ),
)
def main():
  state = me.state(State)
  with me.box(
    style=me.Style(
      display="grid",
      grid_template_columns="1fr 2fr 35fr" if state.menu_open else "1fr 40fr",
      height="100vh",
    )
  ):
    with me.box(
      style=me.Style(
        background=_COLOR_MENU_PANE,
        padding=me.Padding.all(10),
        border=me.Border(
          right=me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid"),
        ),
      )
    ):
      with me.box(
        on_click=toggle_menu,
        style=me.Style(
          align_content="center",
          cursor="pointer",
          margin=me.Margin(bottom=30),
        ),
      ):
        with me.tooltip(message="Close menu" if state.menu_open else "Open menu"):
          me.icon("menu")
      with me.box(
        on_click=open_settings,
        style=me.Style(
          align_content="center",
          cursor="pointer",
          margin=me.Margin.symmetric(vertical=10),
        ),
      ):
        with me.tooltip(message="Settings"):
          me.icon("settings")

      with me.box(
        on_click=on_click_theme_brightness,
        style=me.Style(
          align_content="center",
          cursor="pointer",
          margin=me.Margin.symmetric(vertical=10),
        ),
      ):
        with me.tooltip(
          message="Switch to " + ("light mode" if me.theme_brightness() == "dark" else "dark mode")
        ):
          me.icon("light_mode" if me.theme_brightness() == "dark" else "dark_mode")

    if state.menu_open and state.menu_open_type == "settings":
      with me.box(
        style=me.Style(
          background=_COLOR_MENU,
          padding=me.Padding.all(15),
          border=me.Border(
            right=me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid")
          ),
          display="flex",
          flex_direction="column",
          height="100vh",
        )
      ):
        me.text(
          "Settings",
          style=me.Style(font_weight="bold", margin=me.Margin(bottom=10)),
        )
        me.input(label="API Key", on_input=api_key_input, disabled=state.loading)
        me.select(
          label="Model",
          options=[
            me.SelectOption(
              label="gemini-1.5-flash",
              value="gemini-1.5-flash",
            ),
            me.SelectOption(
              label="gemini-1.5-pro",
              value="gemini-1.5-pro",
            ),
          ],
          value=state.model,
          on_selection_change=on_model_change,
          disabled=state.loading,
        )
        with me.box():
          me.input(
            value=DEFAULT_URL,
            label="URL",
            on_input=url_input,
            style=me.Style(width="100%"),
            disabled=state.loading,
          )
    with me.box(
      style=me.Style(
        background=_COLOR_BG,
        display="flex",
        flex_direction="column",
        flex_grow=1,
        height="100%",
        padding=me.Padding.all(15),
      )
    ):
      with me.box(
        style=me.Style(
          display="grid",
          grid_template_columns="1fr 1fr",
          grid_template_rows="1fr 28fr" if state.error or state.info else "1fr 20fr",
          height="95vh",
          gap=10,
        )
      ):
        if state.error:
          with me.box(style=me.Style(grid_column_start=1, grid_column_end=3)):
            me.text(
              state.error,
              style=me.Style(
                background=me.theme_var("error"),
                color=me.theme_var("on-error"),
                font_weight="bold",
                padding=me.Padding.all(10),
                margin=me.Margin(bottom=10),
              ),
            )
        if state.info:
          with me.box(style=me.Style(grid_column_start=1, grid_column_end=3)):
            me.text(
              state.error,
              style=me.Style(
                background=me.theme_var("secondary"),
                color=me.theme_var("on-secondary"),
                font_weight="bold",
                padding=me.Padding.all(10),
                margin=me.Margin(bottom=10),
              ),
            )

        with me.box(style=me.Style(grid_column_start=1, grid_column_end=3)):
          me.textarea(
            value=state.prompt_placeholder,
            rows=3,
            label="Revise your Mesop app"
            if state.revision_mode
            else "Generate a Mesop app -- The more detailed the better.",
            on_input=on_prompt_input,
            disabled=state.loading,
            style=me.Style(width="100%"),
          )
          with me.box(style=me.Style(display="flex", flex_direction="row")):
            with me.box(
              style=me.Style(
                border=me.Border(
                  right=me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid")
                ),
                padding=me.Padding(right=20),
                margin=me.Margin(right=10),
              )
            ):
              mex.button_toggle(["Generate", "Revision"], selected="Generate")
              # me.slide_toggle(
              #  label="Revision Mode", checked=state.revision_mode, on_change=on_revision_mode
              # )
            with me.box(
              on_click=run_prompt,
              style=me.Style(
                align_content="center",
                cursor="pointer",
                padding=me.Padding.symmetric(horizontal=10),
              ),
            ):
              with me.tooltip(
                message="Revise Mesop app" if state.revision_mode else "Generate Mesop app"
              ):
                me.icon("send")

            with me.box(
              style=me.Style(
                flex_grow=1, display="flex", flex_direction="row", justify_content="end"
              )
            ):
              with me.box(
                on_click=load_url,
                style=me.Style(
                  align_content="center",
                  cursor="pointer",
                  padding=me.Padding.symmetric(horizontal=10),
                ),
              ):
                with me.tooltip(message="Load URL"):
                  me.icon("refresh")
              with me.box(
                on_click=run_code,
                style=me.Style(
                  align_content="center",
                  cursor="pointer",
                  padding=me.Padding.symmetric(horizontal=10),
                ),
              ):
                with me.tooltip(message="Run code"):
                  me.icon("play_arrow")
        with me.box(
          style=me.Style(
            background=me.theme_var("surface-container-lowest"),
            border=me.Border.all(
              me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid")
            ),
            overflow_x="scroll",
            overflow_y="scroll",
          )
        ):
          code_mirror_editor_component(
            code=state.code_placeholder,
            theme="default" if me.theme_brightness() == "light" else "tomorrow-night-eighties",
            on_editor_blur=code_input,
          )

        with me.box():
          me.embed(
            key=str(state.iframe_index),
            src=state.loaded_url or DEFAULT_URL,
            style=me.Style(
              background=me.theme_var("surface-container-lowest"),
              width="100%",
              height="100%",
              border=me.Border.all(me.BorderSide(width=0)),
            ),
          )


def toggle_menu(e: me.ClickEvent):
  s = me.state(State)
  s.menu_open = not s.menu_open


def on_click_theme_brightness(e: me.ClickEvent):
  if me.theme_brightness() == "light":
    me.set_theme_mode("dark")
  else:
    me.set_theme_mode("light")


def open_settings(e: me.ClickEvent):
  s = me.state(State)
  s.menu_open = True
  s.menu_open_type = "settings"


def api_key_input(e: me.InputBlurEvent):
  s = me.state(State)
  s.api_key = e.value


def on_model_change(e: me.SelectSelectionChangeEvent):
  s = me.state(State)
  s.model = e.value


def url_input(e: me.InputBlurEvent):
  s = me.state(State)
  s.url = e.value


def on_revision_mode(e: me.SlideToggleChangeEvent):
  s = me.state(State)
  s.revision_mode = not s.revision_mode


def code_input(e: mel.WebEvent):
  s = me.state(State)
  s.code = e.value["code"]
  s.code_placeholder = e.value["code"]


def load_url(e: me.ClickEvent):
  s = me.state(State)
  s.code_placeholder = s.code
  yield
  s.loaded_url = s.url
  s.iframe_index += 1
  yield


def run_code(e: me.ClickEvent):
  s = me.state(State)
  code = s.code
  s.code_placeholder = s.code
  yield
  result = requests.post(s.url + "exec", data={"code": base64.b64encode(code.encode("utf-8"))})
  if result.status_code == 200:
    yield from load_url(e)
  else:
    s.error = "Failed to upload code"
    yield
    time.sleep(2)
    s.error = ""
    yield


def on_prompt_input(e: me.InputEvent):
  s = me.state(State)
  s.prompt = e.value


def run_prompt(e: me.ClickEvent):
  s = me.state(State)

  s.prompt_placeholder = s.prompt
  yield
  time.sleep(0.4)
  s.prompt_placeholder = ""
  yield

  s.loading = True
  yield

  if s.revision_mode:
    s.code = llm.adjust_mesop_app(s.code, s.prompt, model_name=s.model, api_key=s.api_key)
  else:
    s.code = llm.build_mesop_app(s.prompt, model_name=s.model, api_key=s.api_key)

  s.code = s.code.strip().removeprefix("```python").removesuffix("```")
  s.code_placeholder = s.code
  s.revision_mode = True
  yield

  s.info = (
    "Your code adjustment has been applied!"
    if s.revision_mode
    else "Your Mesop app has been generated!"
  )
  yield
  time.sleep(2)
  s.info = ""
  yield
