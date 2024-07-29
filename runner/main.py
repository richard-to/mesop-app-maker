import mesop as me
import wsgi_app

wsgi = wsgi_app.wsgi_app


@me.page(
  title="PyRun",
  security_policy=me.SecurityPolicy(allowed_iframe_parents=["localhost:*"]),
)
def main():
  me.text("Hello World!")
