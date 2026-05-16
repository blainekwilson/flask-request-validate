"""
Sample Flask Application Demonstrating flask-validate Library

This is a simple registration form application that showcases the use of
flask-request-validate for input validation in Flask applications that are not
using Flask-WTF or API frameworks.

Features demonstrated:
- Form validation with predefined rules (EMAIL, SAFE_USERNAME, etc.)
- Custom rules with set_min_max
- Error handling with HTML responses
- Success page after valid submission
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
    <title>Flask Validate Sample - Registration</title>
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
    <h1>User Registration</h1>
    <p>This sample demonstrates input validation using flask-request-validate.</p>

    <form method="POST" action="/register">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required value="{% if 'username' not in (errors or {}) %}{{ values.get('username','') }}{% endif %}">
            <small>6-20 characters, letters and numbers only</small>
            {% if errors.get('username') %}
                <div class="error">{{ errors['username']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" name="email" id="email" required value="{% if 'email' not in (errors or {}) %}{{ values.get('email','') }}{% endif %}">
            {% if errors.get('email') %}
                <div class="error">{{ errors['email']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>
            <small>Strong password required: 8+ characters, uppercase, lowercase, numbers, and special characters</small>
            {% if errors.get('password') %}
                <div class="error">{{ errors['password']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="state">State (US):</label>
            <input type="text" name="state" id="state" required value="{% if 'state' not in (errors or {}) %}{{ values.get('state','') }}{% endif %}">
            <small>2-letter state code (e.g., CA, NY)</small>
            {% if errors.get('state') %}
                <div class="error">{{ errors['state']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="zip">ZIP Code:</label>
            <input type="text" name="zip" id="zip" required value="{% if 'zip' not in (errors or {}) %}{{ values.get('zip','') }}{% endif %}">
            {% if errors.get('zip') %}
                <div class="error">{{ errors['zip']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="age">Age:</label>
            <input type="number" name="age" id="age" required value="{% if 'age' not in (errors or {}) %}{{ values.get('age','') }}{% endif %}">
            <small>Must be between 18 and 120</small>
            {% if errors.get('age') %}
                <div class="error">{{ errors['age']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="phone">Phone Number:</label>
            <input type="text" name="phone" id="phone" required value="{% if 'phone' not in (errors or {}) %}{{ values.get('phone','') }}{% endif %}">
            <small>US phone number (e.g., 555-123-4567)</small>
            {% if errors.get('phone') %}
                <div class="error">{{ errors['phone']|join(', ') }}</div>
            {% endif %}
        </div>

        <div class="form-group">
            <label for="birthdate">Birth Date:</label>
            <input type="text" name="birthdate" id="birthdate" required value="{% if 'birthdate' not in (errors or {}) %}{{ values.get('birthdate','') }}{% endif %}">
            <small>MM/DD/YYYY format</small>
            {% if errors.get('birthdate') %}
                <div class="error">{{ errors['birthdate']|join(', ') }}</div>
            {% endif %}
        </div>

        {% if errors.get('flask_validate_csrf_token') %}
            <div class="form-group"><div class="error">{{ errors['flask_validate_csrf_token']|join(', ') }}</div></div>
        {% endif %}
        <button type="submit">Register</button>
    </form>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Registration Successful</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1 class="success">Registration Successful!</h1>
    <p>Thank you for registering. Here are the details you submitted:</p>
    <ul>
        <li><strong>Username:</strong> {{ username }}</li>
        <li><strong>Email:</strong> {{ email }}</li>
        <li><strong>State:</strong> {{ state }}</li>
        <li><strong>ZIP:</strong> {{ zip }}</li>
        <li><strong>Age:</strong> {{ age }}</li>
        <li><strong>Phone:</strong> {{ phone }}</li>
        <li><strong>Birth Date:</strong> {{ birthdate }}</li>
    </ul>
    <p><a href="/">Register another user</a></p>
</body>
</html>
"""

@app.route('/')
@fv.exclude_validation("Default home page with registration form")
def home():
    """Display the registration form."""
    return render_template_string(HOME_TEMPLATE, values={}, errors={})

registration_rules = {
    'form': {
        'username': {
            'required': True,
            'rules': fv.SAFE_USERNAME  # 6-20 chars, letters/numbers
        },
        'email': {
            'required': True,
            'rules': fv.EMAIL
        },
        'password': {
            'required': True,
            'rules': fv.PASSWORD_STRONG
        },
        'state': {
            'required': True,
            'rules': fv.US_STATE  # Uses regex for state codes
        },
        'zip': {
            'required': True,
            'rules': fv.US_ZIP
        },
        'age': {
            'required': True,
            'rules': {
                'type': 'int',
                'min': 18,
                'max': 120
            }
        },
        'phone': {
            'required': True,
            'rules': fv.US_PHONE
        },
        'birthdate': {
            'required': True,
            'rules': fv.DATE
        }
    }
}


def on_register_error(result):
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


@app.route('/register', methods=['POST'])
@fv.validate(registration_rules, on_error=on_register_error)
def register():
    """Handle registration form submission with validation."""
    # If we reach here, validation passed
    username = request.form['username']
    email = request.form['email']
    state = request.form['state']
    zip_code = request.form['zip']
    age = request.form['age']
    phone = request.form['phone']
    birthdate = request.form['birthdate']

    # In a real app, you'd save to database here
    # For demo, just show success page

    return render_template_string(SUCCESS_TEMPLATE,
                                username=username,
                                email=email,
                                state=state,
                                zip=zip_code,
                                age=age,
                                phone=phone,
                                birthdate=birthdate)

@app.route('/display_email', methods=['GET'])
def display_email():
    """Example of an unprotected route that should be caught by security monitoring."""
    email = request.args.get('email', 'No email provided')
    return f"<h1>Email: {email}</h1>"

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

    print("\n🌐 Visit http://127.0.0.1:5000/ to see the registration form.")
    print("🌐 Visit http://127.0.0.1:5000/security-status to see route security status")
    print("Try submitting invalid data to see validation errors.")
    app.run(debug=True)