"""
Minimal Flask **fixture app** (not a unittest module) for ``test_my_perf``.

Single POST route with ``SAFE_ALPHA`` on ``name``. Used for repeated successful
validation without the full route matrix in ``sample_app.py``.
"""

import os
import sys

from flask import Flask, request, Response, render_template_string

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import flask_request_validate as fv

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

FORM = '''
<!DOCTYPE html> 
<html> 
<head> 
    <title>My Form</title> 
</head> 
<body> 
    <h1>My Form</h1> 
    <form method="post" action="/" enctype="multipart/form-data"> 
        <p><label for="name">Name</label>
        <input id="name" maxlength="10" minlength="2" name="name" required type="text" value=""></p>
        <p><input type="submit" value="Submit"></p> 
    </form> 
</body> 
</html>'''

# root directory
@app.route('/', methods=['GET'])
def get_root() -> Response:
    '''
    displays the tests
    '''
    return render_template_string(FORM)


@app.route('/', methods=['POST'])
@fv.validate({
            'form': {
                    'name': {'required': True, 'rules': fv.SAFE_ALPHA}
            }
        })
def index() -> Response:
    """Echo ``name`` when POST passes validation (letters-only, length 2–10)."""
    if request.method == 'POST':
        return f'<html><body>Name: {request.form["name"]}</body></html>'

    return FORM


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()
