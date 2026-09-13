"""
Simple Flask example that demonstrates the default HTML error response
returned by the `flask-request-validate` decorator when validation fails.

Run this and submit invalid data to see the library's default formatted
HTML error page (400 response).
"""

from flask import Flask, request, render_template
import sys
import os

# Add the src directory to the path to import flask_request_validate
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import flask_request_validate as fv

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('default_error_form.html')


@app.route('/submit', methods=['POST'])
@fv.validate({
    'form': {
        'name': {
            'required': True,
            'rules': {
                'type': 'str',
                'min': 2,
                'max': 50,
            }
        },
        'age': {
            'required': True,
            'rules': {
                'type': 'int',
                'min': 18,
                'max': 120,
            }
        }
    }
})
def submit():
    # If validation passes, return a simple success message.
    name = request.form['name']
    age = request.form['age']
    return f"Received: {name} (age {age})"


if __name__ == '__main__':
    print("Run: python examples/example_default_error_response.py")
    app.run(debug=True)
