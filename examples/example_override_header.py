"""
Example script that demonstrates overriding one of the security header defaults
before creating the Flask app. Run this script to start a small server that
returns headers showing the overridden value.

Usage:
    python examples/example_override_header.py

Then visit http://127.0.0.1:5001/ and inspect the response headers.
"""
import sys
import os

# Add the src directory to the path to import flask_request_validate
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import flask_request_validate as fv
from flask import Flask

# Override a module-level default before creating the app
fv.SECURITY_HEADER_DEFAULTS['X-Frame-Options']['value'] = 'SAMEORIGIN'

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Override Example</h1>'

if __name__ == '__main__':
    print('Starting example app with X-Frame-Options =', fv.SECURITY_HEADER_DEFAULTS['X-Frame-Options']['value'])
    app.run(port=5001)
