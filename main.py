import base64
import time

import requests
import mesop as me
import mesop.labs as mel

import components as mex
import handlers
import llm
from constants import (
  PROMPT_MODE_REVISE,
  PROMPT_MODE_GENERATE,
  HELP_TEXT,
  TEMPLATES,
  EXAMPLE_CHAT_PROMPTS,
)
from state import State
from web_components import code_mirror_editor_component
from web_components import AsyncAction
from web_components import async_action_component


@me.page(
  title="Mesop App Maker",
  stylesheets=[
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/theme/tomorrow-night-eighties.min.css",
  ],
  security_policy=me.SecurityPolicy(
    allowed_iframe_parents=["https://huggingface.co"],
    allowed_connect_srcs=[
      "https://cdnjs.cloudflare.com",
      "*.fonts.gstatic.com",
    ],
    allowed_script_srcs=[
      "https://cdn.jsdelivr.net",
      "https://cdnjs.cloudflare.com",
      "*.fonts.gstatic.com",
    ],
  ),
)
def main():
  state = me.state(State)

  action = (
    AsyncAction(value=state.async_action_name, duration_seconds=state.async_action_duration)
    if state.async_action_name
    else None
  )
  async_action_component(action=action, on_finished=on_async_action_finished)

  # Status snackbar
  mex.snackbar(
    label=state.info,
    is_visible=state.show_status_snackbar,
  )

  # Error dialog
  with mex.dialog(state.show_error_dialog):
    me.text("Failed to upload code", type="headline-6")
    with me.box(
      style=me.Style(max_width=500, max_height=300, overflow_x="scroll", overflow_y="scroll")
    ):
      me.code(
        state.error.replace("\n", "  \n"),
      )
    with mex.dialog_actions():
      me.button(
        "Close",
        key="show_error_dialog",
        on_click=handlers.on_hide_component,
      )

  # New file dialog
  with mex.dialog(state.show_new_dialog):
    me.text("Select a template", type="headline-6")
    me.select(
      label="Template",
      key="template-selector-" + str(state.select_index),
      options=[
        me.SelectOption(label="Default", value="default.txt"),
        me.SelectOption(label="Basic Chat", value="basic_chat.txt"),
        me.SelectOption(label="Advanced Chat", value="advanced_chat.txt"),
      ],
      on_selection_change=on_select_template,
    )
    with mex.dialog_actions():
      me.button(
        "Close",
        key="show_new_dialog",
        on_click=handlers.on_hide_component,
      )

  # Help dialog
  with mex.dialog(state.show_help_dialog):
    me.text("Usage Instructions", type="headline-6")
    me.markdown(HELP_TEXT)
    me.link(
      text="See Github repository for full instructions.",
      url="https://github.com/richard-to/mesop-app-runner",
      open_in_new_tab=True,
      style=me.Style(color=me.theme_var("primary")),
    )
    with mex.dialog_actions():
      me.button(
        "Close",
        key="show_help_dialog",
        on_click=handlers.on_hide_component,
      )

  # Generate code panel
  with mex.panel(
    is_open=state.show_generate_panel,
    title="Generate Code",
    on_click_close=handlers.on_hide_component,
    key="generate_panel",
  ):
    mex.button_toggle(
      [PROMPT_MODE_GENERATE, PROMPT_MODE_REVISE],
      selected=state.prompt_mode,
      on_click=on_click_prompt_mode,
    )

    me.select(
      label="App type",
      key="prompt_app_type",
      value=state.prompt_app_type,
      options=[
        me.SelectOption(label="General", value="general"),
        me.SelectOption(label="Chat", value="chat"),
      ],
      style=me.Style(width="100%", margin=me.Margin(top=30)),
      on_selection_change=handlers.on_update_selection,
    )

    me.textarea(
      value=state.prompt_placeholder,
      rows=10,
      label="What changes do you want to make?"
      if state.prompt_mode == PROMPT_MODE_REVISE
      else "What do you want to make?",
      key="prompt",
      on_blur=handlers.on_update_input,
      disabled=state.loading,
      style=me.Style(width="100%", margin=me.Margin(top=15)),
    )

    with me.tooltip(message="Generate app"):
      with me.content_button(on_click=on_run_prompt, type="flat", disabled=state.loading):
        me.icon("send")

    if state.prompt_mode == "Generate" and state.prompt_app_type == "chat":
      me.text("Example prompts", type="headline-6", style=me.Style(margin=me.Margin(top=15)))

      for index, chat_prompt in enumerate(EXAMPLE_CHAT_PROMPTS):
        with me.box(
          key=f"example_prompt-{index}",
          on_click=on_click_example_prompt,
          style=me.Style(
            background=me.theme_var("surface-container"),
            border=me.Border.all(
              me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid")
            ),
            border_radius=5,
            cursor="pointer",
            margin=me.Margin.symmetric(vertical=10),
            padding=me.Padding.all(10),
            text_overflow="ellipsis",
          ),
        ):
          me.text(_truncate_text(chat_prompt))

  # Prompt history panel
  with mex.panel(
    is_open=state.show_prompt_history_panel,
    title="Prompt History",
    on_click_close=handlers.on_hide_component,
    key="prompt_history_panel",
  ):
    for prompt_history in reversed(state.prompt_history):
      with me.box(
        key=f"prompt-{prompt_history['index']}",
        on_click=on_click_history_prompt,
        style=me.Style(
          background=me.theme_var("surface-container"),
          border=me.Border.all(
            me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid")
          ),
          border_radius=5,
          cursor="pointer",
          margin=me.Margin.symmetric(vertical=10),
          padding=me.Padding.all(10),
          text_overflow="ellipsis",
        ),
      ):
        me.text(prompt_history["mode"], style=me.Style(font_weight="bold", font_size=13))
        me.text(_truncate_text(prompt_history["prompt"]))

  with me.box(
    style=me.Style(
      display="grid",
      grid_template_columns="1fr 2fr 35fr" if state.menu_open else "1fr 40fr",
      height="100vh",
    )
  ):
    with me.box(
      style=me.Style(
        background=me.theme_var("surface-container"),
        padding=me.Padding.all(10),
        border=me.Border(
          right=me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid"),
        ),
      )
    ):
      mex.toolbar_button(
        icon="menu",
        tooltip="Close menu" if state.menu_open else "Open menu",
        on_click=on_toggle_sidebar_menu,
      )

      mex.toolbar_button(
        icon="settings",
        tooltip="Settings",
        on_click=on_open_settings,
      )

      mex.toolbar_button(
        icon="light_mode" if me.theme_brightness() == "dark" else "dark_mode",
        tooltip="Switch to " + ("light mode" if me.theme_brightness() == "dark" else "dark mode"),
        on_click=on_click_theme_brightness,
      )

      mex.toolbar_button(
        icon="help",
        tooltip="Help",
        key="show_help_dialog",
        on_click=handlers.on_show_component,
      )

    if state.menu_open and state.menu_open_type == "settings":
      with me.box(
        style=me.Style(
          background=me.theme_var("surface-container-low"),
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
        me.input(
          type="password",
          label="Gemini API Key",
          key="api_key",
          value=state.api_key,
          on_blur=handlers.on_update_input,
          disabled=state.loading,
        )
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
          key="model",
          value=state.model,
          on_selection_change=handlers.on_update_selection,
          disabled=state.loading,
        )
        with me.box():
          me.input(
            value=state.runner_url,
            label="Runner URL",
            key="runner_url",
            on_blur=handlers.on_update_input,
            style=me.Style(width="100%"),
            disabled=state.loading,
          )
        with me.box():
          me.input(
            type="password",
            value=state.runner_token,
            label="Runner Token",
            key="runner_token",
            on_blur=handlers.on_update_input,
            style=me.Style(width="100%"),
            disabled=state.loading,
          )

    # Main content
    with me.box(
      style=me.Style(
        background=me.theme_var("surface-container-lowest"),
        display="flex",
        flex_direction="column",
        flex_grow=1,
        height="100%",
      )
    ):
      # Toolbar
      with me.box(
        style=me.Style(
          display="grid",
          grid_template_columns="1fr 1fr",
          grid_template_rows="1fr 20fr",
          height="calc(100vh - 5px)",
        )
      ):
        with me.box(
          style=me.Style(
            grid_column_start=1,
            grid_column_end=3,
            background=me.theme_var("surface-container"),
            padding=me.Padding.all(5),
            border=me.Border(
              bottom=me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid"),
            ),
          )
        ):
          with me.box(style=me.Style(display="flex", flex_direction="row")):
            with me.box(
              style=me.Style(
                flex_grow=1,
                display="flex",
                flex_direction="row",
              )
            ):
              mex.toolbar_button(
                icon="add",
                tooltip="New file",
                key="show_new_dialog",
                on_click=handlers.on_show_component,
              )

              mex.toolbar_button(
                icon="bolt",
                tooltip="Generate code",
                key="show_generate_panel",
                on_click=on_show_generate_panel,
              )

              if state.prompt_history:
                mex.toolbar_button(
                  icon="history",
                  tooltip="Prompt history",
                  key="show_prompt_history_panel",
                  on_click=on_show_prompt_history_panel,
                )

            with me.box(
              style=me.Style(
                flex_grow=1, display="flex", flex_direction="row", justify_content="end"
              )
            ):
              mex.toolbar_button(
                icon="refresh",
                tooltip="Load URL",
                on_click=on_load_url,
              )
              mex.toolbar_button(
                icon="play_arrow",
                tooltip="Run code",
                on_click=on_run_code,
              )

        # Code editor pane
        with me.box(
          style=me.Style(
            background=me.theme_var("surface-container-lowest"),
            overflow_x="scroll",
            overflow_y="scroll",
          )
        ):
          code_mirror_editor_component(
            code=state.code_placeholder,
            theme="default" if me.theme_brightness() == "light" else "tomorrow-night-eighties",
            on_editor_blur=on_code_input,
          )

        # App preview pane
        with me.box():
          me.embed(
            key=str(state.iframe_index),
            src=state.loaded_url,
            style=me.Style(
              background=me.theme_var("surface-container-lowest"),
              width="100%",
              height="100%",
              border=me.Border.all(me.BorderSide(width=0)),
            ),
          )


def on_toggle_sidebar_menu(e: me.ClickEvent):
  """Toggles sidebar menu expansion."""
  state = me.state(State)
  state.menu_open = not state.menu_open


def on_click_theme_brightness(e: me.ClickEvent):
  """Toggles dark mode."""
  if me.theme_brightness() == "light":
    me.set_theme_mode("dark")
  else:
    me.set_theme_mode("light")


def on_open_settings(e: me.ClickEvent):
  """Shows settings menu."""
  state = me.state(State)
  state.menu_open = True
  state.menu_open_type = "settings"


def on_click_prompt_mode(e: me.ClickEvent):
  """Toggles prompt modes - generate / revision."""
  state = me.state(State)
  state.prompt_mode = (
    PROMPT_MODE_REVISE if state.prompt_mode == PROMPT_MODE_GENERATE else PROMPT_MODE_GENERATE
  )


def on_click_example_prompt(e: me.ClickEvent):
  """Populates chat box with example prompt."""
  state = me.state(State)
  _, index = e.key.split("-")
  state.prompt = EXAMPLE_CHAT_PROMPTS[int(index)]
  state.prompt_placeholder = state.prompt


def on_code_input(e: mel.WebEvent):
  """Captures code input into state on blur."""
  state = me.state(State)
  state.code = e.value["code"]
  state.code_placeholder = e.value["code"]


def on_load_url(e: me.ClickEvent):
  """Loads the Mesop app page into the iframe."""
  state = me.state(State)
  state.code_placeholder = state.code
  yield
  state.loaded_url = state.runner_url.removesuffix("/") + state.runner_url_path
  state.iframe_index += 1
  yield


def on_run_code(e: me.ClickEvent):
  """Tries to upload code to the Mesop app Runner."""
  state = me.state(State)
  state.code_placeholder = state.code
  yield
  result = requests.post(
    state.runner_url.removesuffix("/") + "/exec",
    data={"token": state.runner_token, "code": base64.b64encode(state.code.encode("utf-8"))},
  )
  if result.status_code == 200:
    state.runner_url_path = result.content.decode("utf-8")
    yield from on_load_url(e)
  else:
    state.show_error_dialog = True
    state.error = result.content.decode("utf-8")
    yield


def on_run_prompt(e: me.ClickEvent):
  """Generate code from prompt."""
  state = me.state(State)
  if not state.prompt:
    return

  state.prompt_placeholder = state.prompt
  yield
  time.sleep(0.4)
  state.prompt_placeholder = ""
  yield

  state.loading = True
  yield

  if state.prompt_mode == PROMPT_MODE_REVISE:
    state.code = llm.adjust_mesop_app(
      state.code,
      state.prompt,
      model_name=state.model,
      api_key=state.api_key,
      app_type=state.prompt_app_type,
    )
  else:
    state.code = llm.generate_mesop_app(
      state.prompt, model_name=state.model, api_key=state.api_key, app_type=state.prompt_app_type
    )

  state.code = state.code.strip().removeprefix("```python").removesuffix("```")
  state.code_placeholder = state.code
  state.info = (
    "Your code adjustment has been applied!"
    if state.prompt_mode == PROMPT_MODE_REVISE
    else "Your Mesop app has been generated!"
  )
  state.prompt_history.append(
    dict(
      prompt=state.prompt,
      code=state.code,
      index=len(state.prompt_history),
      mode=state.prompt_mode,
      app_type=state.prompt_app_type,
    )
  )

  state.prompt_mode = PROMPT_MODE_REVISE
  state.loading = False
  yield

  state.show_status_snackbar = True
  state.async_action_name = "hide_status_snackbar"
  yield


def on_select_template(e: me.SelectSelectionChangeEvent):
  """Update editor with selected template"""
  state = me.state(State)
  state.code_placeholder = TEMPLATES[e.value]
  state.code = TEMPLATES[e.value]
  state.show_new_dialog = False
  state.select_index += 1


def on_show_prompt_history_panel(e: me.ClickEvent):
  """Show prompt history panel"""
  state = me.state(State)
  state.show_prompt_history_panel = True
  state.show_generate_panel = False


def on_show_generate_panel(e: me.ClickEvent):
  """Show generate panel and focus on prompt text area"""
  state = me.state(State)
  state.show_generate_panel = True
  state.show_prompt_history_panel = False
  yield
  me.focus_component(key="prompt")
  yield


def on_click_history_prompt(e: me.ClickEvent):
  """Set previous prompt/code"""
  state = me.state(State)
  index = int(e.key.replace("prompt-", ""))
  prompt_history = state.prompt_history[index]
  state.prompt_placeholder = prompt_history["prompt"]
  state.prompt = state.prompt_placeholder
  state.code_placeholder = prompt_history["code"]
  state.code = state.code_placeholder
  state.prompt_app_type = prompt_history["app_type"]
  state.prompt_mode = prompt_history["mode"]
  state.show_prompt_history_panel = False
  state.show_generate_panel = True
  yield
  me.focus_component(key="prompt")
  yield


def on_async_action_finished(e: mel.WebEvent):
  state = me.state(State)
  state.async_action_name = ""
  state.info = ""
  state.show_status_snackbar = False


def _truncate_text(text, char_limit=100):
  """Truncates text that is too long."""
  if len(text) <= char_limit:
    return text
  truncated_text = text[:char_limit].rsplit(" ", 1)[0]
  return truncated_text.rstrip(".,!?;:") + "..."
