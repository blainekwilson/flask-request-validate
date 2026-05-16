"""
Sample Flask Application Demonstrating flask-validate Library

This is a simple login form application that showcases missing form field validation.

Features demonstrated:
- Form validation with predefined rules (SAFE_USERNAME)
- Missing field validation (password)
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
# Sessions are required for CSRF token storage. Set a secret key for example/demo use.
# In production, set a secure, random secret and keep it secret.
app.secret_key = 'dev-secret-change-me'

# Example of using security monitoring
@app.route('/security-status', methods=['GET'])
@fv.exclude_validation("Security status endpoint")
def security_status():
    """Show the current security status of all routes."""
    status = fv.get_route_security_status()
    return f"""
    <h2>Route Security Status</h2>
    <p>Protected routes: {status['protected_count']}</p>
    <p>Excluded routes: {status['excluded_count']}</p>
    <p>Unprotected routes: {status['unprotected_count']}</p>
    <h3>Protected:</h3>
    <ul>{''.join(f'<li>{route}</li>' for route in status['protected'])}</ul>
    <h3>Excluded:</h3>
    <ul>{''.join(f'<li>{route}</li>' for route in status['excluded'])}</ul>
    <h3>Unprotected:</h3>
    <ul>{''.join(f'<li>{route}</li>' for route in status['unprotected'])}</ul>
    """

# HTML Templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Validate Sample - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input { width: 300px; padding: 8px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-top: 4px; }
    </style>
</head>
<body>
    <h1>User Login</h1>
    <p>This sample demonstrates a misconfigured form against flask-request-validate.
    The password field is missing validation rules causing flask-request-validate to fail the validation.</p>

    <form method="POST" action="/login">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required value="{% if 'username' not in (errors or {}) %}{{ values.get('username','') }}{% endif %}">
            <small>6-20 characters, letters and numbers only</small>
            {% if errors.get('username') %}
                <div class="error">{{ errors['username']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>
            <small>Extra field with no validation rules.</small>
            {% if errors.get('password') %}
                <div class="error">{{ errors['password']|join(', ') }}</div>
            {% endif %}
        </div>

        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login Successful</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1 class="success">Login Successful!</h1>
    <p>Thank you for logging in. Here are the details you submitted:</p>
    <ul>
        <li><strong>Username:</strong> {{ username }}</li>
    </ul>
    <p><a href="/">Login another user</a></p>
</body>
</html>
"""

@app.route('/')
@fv.exclude_validation("Default home page with login form")
def home():
    """Display the registration form."""
    return render_template_string(HOME_TEMPLATE, values={}, errors={})

registration_rules = {
    'form': {
        'username': {
            'required': True,
            'rules': fv.SAFE_USERNAME  # 6-20 chars, letters/numbers
        }
    }
}


def on_login_error(result):
    """Custom on_error handler that re-renders the form with only validated (safe) values
    and presents error messages next to offending fields. Any field that failed validation
    will NOT have its original value reinserted into the page.
    """
    errors = result.get('errors', {}) or {}

    # Build a dict of only the validated values: present in rules and not listed in errors
    sanitized = {}
    form_rules = registration_rules.get('form', {})
    for key in form_rules:
        if key in request.form and key not in errors:
            sanitized[key] = request.form.get(key)

    # Render the home template with `values` and `errors`
    resp = render_template_string(HOME_TEMPLATE, values=sanitized, errors=errors)
    return resp, 400


@app.route('/login', methods=['POST'])
@fv.validate(registration_rules, on_error=on_login_error)
def register():
    """Handle registration form submission with validation."""
    # If we reach here, validation passed
    username = request.form['username']

    # In a real app, you'd save to database here
    # For demo, just show success page

    return render_template_string(SUCCESS_TEMPLATE, username=username)

if __name__ == '__main__':
    print("🚀 Starting Flask Validate Sample Application with security monitoring...")

    # Check for unprotected routes before starting
    try:
        result = fv.check_unprotected_routes(app, warn_unprotected=True, fail_on_unprotected=False)
        print("✅ Security check complete:")
        print(f"   Protected routes: {len(result['protected'])}")
        print(f"   Excluded routes: {len(result['excluded'])}")
        print(f"   Unprotected routes: {len(result['unprotected'])}")

        if result['unprotected']:
            print("\n⚠️  Unprotected routes detected:")
            for route in result['unprotected']:
                print(f"   - {route['endpoint']}")

    except Exception as e:
        print(f"❌ Security check failed: {e}")

    print("\n🌐 Visit http://127.0.0.1:5000/ to see the login form.")
    print("🌐 Visit http://127.0.0.1:5000/security-status to see route security status")
    print("Try submitting invalid data to see validation errors.")
    app.run(debug=True)