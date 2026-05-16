# Usage & Examples

Basic decorator usage:

```python
from flask import Flask, request
import flask_request_validate as fv

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
@fv.validate({
    'form': {
        'email': {'required': True, 'rules': fv.EMAIL}
    }
})
def submit():
    return request.form['email']
```

Using a custom error handler (`on_error`):

```python
def my_handler(result):
    # result is the full validation result dict; return any Flask response
    return jsonify({'errors': result['errors']}), 400

@app.route('/submit_json', methods=['POST'])
@fv.validate({
    'form': {
        'email': {'required': True, 'rules': fv.EMAIL}
    }
}, on_error=my_handler)
def submit_json():
    return request.form['email']
```

Notes about the validation result:

- `result['valid']` is a boolean.
- `result['errors']` is a dictionary mapping field names to lists of error messages.
- The default HTML formatter includes field prefixes (e.g. `email: Invalid email address`).

Examples directory contains working demos, including `example_on_error.py` which shows a small UI and custom `on_error` handler.
