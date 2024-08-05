import base64
import os
import secrets
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable

from absl import flags
from flask import Flask
from flask import request

from mesop.cli.execute_module import execute_module
from mesop.runtime import enable_debug_mode
from mesop.runtime import reset_runtime
from mesop.runtime import hot_reload_finished
from mesop.server.constants import PROD_PACKAGE_PATH
from mesop.server.flags import port
from mesop.server.logging import log_startup
from mesop.server.server import configure_flask_app
from mesop.server.static_file_serving import configure_static_file_serving

PAGE_EXPIRATION_MINUTES = 10
MAIN_MODULE = "main"


@dataclass(frozen=True)
class RegisteredModule:
  name: str = ""
  created_at: datetime = field(default_factory=lambda: datetime.now())


registered_modules = set([RegisteredModule(MAIN_MODULE)])


class App:
  _flask_app: Flask

  def __init__(self, flask_app: Flask):
    self._flask_app = flask_app

  def run(self):
    log_startup(port=port())
    self._flask_app.run(host="::", port=port(), use_reloader=False)


def create_app(prod_mode: bool, run_block: Callable[..., None] | None = None) -> App:
  flask_app = configure_flask_app(prod_mode=prod_mode)

  # Enable debug mode so we can see errors with the code we're running.
  enable_debug_mode()

  if run_block is not None:
    run_block()

  configure_static_file_serving(flask_app, static_file_runfiles_base=PROD_PACKAGE_PATH)

  @flask_app.route("/exec", methods=["POST"])
  def exec_route():
    global registered_modules

    param = request.form.get("code")
    new_module = RegisteredModule()
    if param is None:
      raise Exception("Missing request parameter")
    try:
      new_module = RegisteredModule(f"page_{secrets.token_urlsafe(8)}")

      # Create a new page with the code to run
      # We expect `@me.page()` here for this to work.
      code = base64.urlsafe_b64decode(param)
      code = code.decode("utf-8").replace(
        "@me.page()",
        f'@me.page(path="/{new_module.name}", security_policy=me.SecurityPolicy(allowed_iframe_parents=["localhost:*"]))',
      )
      with open(f"{new_module.name}.py", "w") as file:
        file.write(code)

      # Add new registered path
      registered_modules.add(new_module)

      # Clean up old registered paths (except main)
      registered_modules_to_delete = set()
      for registered_module in registered_modules:
        if (
          registered_module.name != MAIN_MODULE
          and registered_module.created_at
          < datetime.now() - timedelta(minutes=PAGE_EXPIRATION_MINUTES)
        ):
          registered_modules_to_delete.add(registered_module)
      registered_modules -= registered_modules_to_delete

      # Manually hot reload
      reset_runtime()
      for module in registered_modules:
        execute_module(module_path=make_path_absolute(f"{module.name}.py"), module_name=module.name)
      hot_reload_finished()

    except Exception:
      # If there was an error, it's likely that the code failed during hot reload, so
      # we need to trigger another hot reload without the bad code.
      if registered_module in registered_modules:
        registered_modules.remove(registered_module)
        reset_runtime()
        for registered_module in registered_modules:
          execute_module(
            module_path=make_path_absolute(f"{registered_module.name}.py"),
            module_name=registered_module.name,
          )
        hot_reload_finished()
      # Get the current exception information
      exc_type, exc_value, exc_traceback = sys.exc_info()
      # Format the traceback as a string
      tb_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
      return tb_string, 500

    # Return the page path that's running the new code, so we can update the iframe with
    # the right path.
    return f"/{new_module.name}"

  return App(flask_app=flask_app)


_app = None


def wsgi_app(environ: dict[Any, Any], start_response: Callable[..., Any]):
  global _app
  if not _app:
    flags.FLAGS(sys.argv[:1])
    _app = create_app(prod_mode=True)
  return _app._flask_app.wsgi_app(environ, start_response)


def make_path_absolute(file_path: str):
  if os.path.isabs(file_path):
    return file_path
  absolute_path = os.path.join(os.getcwd(), file_path)
  return absolute_path
