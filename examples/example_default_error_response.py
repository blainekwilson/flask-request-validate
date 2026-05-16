"""
Simple Flask example that demonstrates the default HTML error response
returned by the `flask-request-validate` decorator when validation fails.

Run this and submit invalid data to see the library's default formatted
HTML error page (400 response).
"""

from flask import Flask, request, render_template_string
import sys
import os

# Add the src directory to the path to import flask_request_validate
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import flask_request_validate as fv

app = Flask(__name__)

FORM = """
<!doctype html>
<html>
  <head><title>Default Validator HTML Example</title></head>
  <body>
    <h1>Default Error Response Demo</h1>
    <form method="POST" action="/submit">
      <label for="name">Name (2-50 chars):</label>
      <input id="name" name="name" type="text" required>
      <br/>
      <label for="age">Age (integer 18-120):</label>
      <input id="age" name="age" type="number" required>
      <br/>
      <button type="submit">Submit</button>
    </form>
  </body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(FORM)


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
