import mesop as me

from state import State


def on_show_component(e: me.ClickEvent):
  """Generic event to show a component."""
  state = me.state(State)
  setattr(state, e.key, True)


def on_hide_component(e: me.ClickEvent):
  """Generic event to hide a component."""
  state = me.state(State)
  setattr(state, e.key, False)


def on_update_input(e: me.InputBlurEvent | me.InputEvent | me.InputEnterEvent):
  """Generic event to update input values."""
  state = me.state(State)
  setattr(state, e.key, e.value)


def on_update_selection(e: me.SelectSelectionChangeEvent):
  """Generic event to update input values."""
  state = me.state(State)
  setattr(state, e.key, e.value)
