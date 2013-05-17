import sys
import logging
from urlparse import urlunsplit
from flask.app import Flask
from flask.globals import request
from werkzeug.utils import redirect
from distance import MirrorDistance
from models import Mirror
from logging import getLogger

log = getLogger(__name__)


app = Flask(__name__)
app.config.from_object("config.Config")


@app.route("/")
def index():
    ret = str(list(Mirror.objects.filter(age__lt=3601)))
    return "ok " + ret


@app.route("/simple/<path:path>")
def proxy(path):
    mirror = MirrorDistance().get_nearest_mirror(request.remote_addr)
    url = urlunsplit((
        "http",
        mirror,
        "simple/{}".format(path),
        request.query_string,
        None
    ))
    log.debug("Redirecting to %s", url)
    return redirect(url)


if __name__ == "__main__":
    app.run("0.0.0.0", 8000, debug=True)
