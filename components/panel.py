from typing import Callable

import mesop as me


@me.content_component
def panel(is_open: bool, title: str, on_click_close: Callable | None = None, key: str = ""):
  """Slide-in panel from right side."""
  with me.box(
    style=me.Style(
      display="block" if is_open else "none",
      height="100%",
      overflow_x="auto",
      overflow_y="auto",
      pointer_events="none",
      position="fixed",
      width="100%",
      z_index=1000,
    )
  ):
    with me.box(
      style=me.Style(
        align_items="center",
        display="grid",
        height="calc(100vh - 10px)",
        justify_items="end",
      )
    ):
      with me.box(
        style=me.Style(
          background=me.theme_var("surface-container-low"),
          border_radius=5,
          box_sizing="border-box",
          border=me.Border.all(
            me.BorderSide(width=1, color=me.theme_var("outline-variant"), style="solid"),
          ),
          margin=me.Margin(top=10, right=5),
          padding=me.Padding.all(20),
          pointer_events="auto",
          height="100%",
          width="30%",
        )
      ):
        with me.box(
          style=me.Style(
            align_items="center",
            display="flex",
            justify_content="space-between",
            margin=me.Margin(bottom=15),
          ),
        ):
          me.text(title, style=me.Style(font_size=16, font_weight="bold"))
          with me.box(key=f"show_{key}", on_click=on_click_close, style=me.Style(cursor="pointer")):
            me.icon("close")

        me.slot()
