import os
import datetime
import json
from functools import wraps

from flask import Flask, redirect, request, current_app

# Create application object
app = Flask(__name__)

app.config.from_object('cc_web.defaults')
app.config.from_envvar('APPLICATION_SETTINGS', silent=True)

import sys

# Create logging
if app.config.get('LOG_FILE') == True:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('logs/cc_web.txt')
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

# from https://gist.github.com/aisipos/1094140
def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function

# Import everything
import cc_web.views

