"""
Simple example showing use of `on_error` with the validation decorator.

Run this example and POST to `/demo_on_error` without an `email` form
field to see the custom handler return a modified message.
"""
import os
import sys
from flask import Flask, request, Response, render_template_string

# Ensure src is on the path to import the package from this workspace
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import flask_request_validate as fv

app = Flask(__name__)


def custom_error_handler(validation_result):
    """Return a plain-text message showing the custom handler was used."""
    errors = validation_result.get('errors', [])
    msg = 'Custom error handler triggered. Errors: ' + '; '.join(errors)
    return Response(msg, status=400, mimetype='text/plain')


@app.route('/demo_on_error', methods=['POST'])
@fv.validate({
    'form': {
        'email': {'required': True, 'rules': fv.EMAIL}
    }
}, on_error=custom_error_handler)
def demo_on_error():
    """Echo the submitted email when validation succeeds."""
    return f"Success: {request.form['email']}"


@app.route('/', methods=['GET'])
def demo_on_error_form():
        """Simple HTML form to exercise the demo_on_error endpoint."""
        tpl = '''
        <html>
            <head><title>Demo on_error</title></head>
            <body>
                <h2>Demo: custom on_error handler</h2>
                <form method="post" action="/demo_on_error">
                    <label for="email">Email:</label>
                    <input type="text" id="email" name="email" />
                    <button type="submit">Submit</button>
                </form>
                <p>Submit without an email to see the custom error handler response.</p>
            </body>
        </html>
        '''
        return render_template_string(tpl)


if __name__ == '__main__':
    app.run(debug=True)
