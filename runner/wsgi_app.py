import base64
import os
import sys
import traceback
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


class App:
  _flask_app: Flask

  def __init__(self, flask_app: Flask):
    self._flask_app = flask_app

  def run(self):
    log_startup(port=port())
    self._flask_app.run(host="::", port=port(), use_reloader=False)


def create_app(prod_mode: bool, run_block: Callable[..., None] | None = None) -> App:
  flask_app = configure_flask_app(prod_mode=prod_mode)

  enable_debug_mode()

  if run_block is not None:
    run_block()

  configure_static_file_serving(flask_app, static_file_runfiles_base=PROD_PACKAGE_PATH)

  @flask_app.route("/exec", methods=["POST"])
  def exec_route():
    param = request.form.get("code")
    if param is None:
      raise Exception("Missing request parameter")
    try:
      code = base64.urlsafe_b64decode(param)
      with open("main.py", "w") as file:
        file.write(code.decode("utf-8"))
      reset_runtime()
      execute_module(module_path=make_path_absolute("main.py"), module_name="main")
      hot_reload_finished()
    except Exception:
      # Get the current exception information
      exc_type, exc_value, exc_traceback = sys.exc_info()
      # Format the traceback as a string
      tb_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
      return tb_string, 500
    return "OK"

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
