"""
Flask Application Demonstrating Protected, Excluded, and Unprotected Endpoints

This example showcases three different categories of endpoints:

1. PROTECTED ENDPOINTS - Use @validate decorator to enforce input validation
   - Form submissions must pass validation rules
   - Invalid requests receive error responses with details

2. EXCLUDED ENDPOINTS - Use @exclude_validation decorator to skip validation
   - Endpoints that don't require input validation (read-only pages, status checks)
   - Marked as safe and intentionally excluded

3. UNPROTECTED ENDPOINTS - Regular Flask routes without any validation decorator
   - No validation enforced
   - Can accept any input without restrictions

The root endpoint "/" displays a comprehensive report of all endpoints and their
validation status.
"""

import os
import sys
from flask import Flask, request, render_template_string, jsonify

# Ensure src is on the path to import the package from this workspace
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import flask_request_validate as fv

app = Flask(__name__)
# Sessions are required for CSRF token storage. Set a secret key for example/demo use.
# In production, set a secure, random secret and keep it secret.
app.secret_key = 'dev-secret-change-me'


# ============================================================================
# PROTECTED ENDPOINTS - These require valid input
# ============================================================================

@app.route('/contact', methods=['GET', 'POST'])
@fv.validate({
    'form': {
        'name': {'required': True, 'rules': fv.SAFE_TEXT},
        'email': {'required': True, 'rules': fv.EMAIL},
        'message': {'required': True, 'rules': fv.SAFE_TEXT}
    }
})
def contact():
    """Protected endpoint: Contact form that validates all inputs."""
    if request.method == 'POST':
        return f"""
        <h2>Thank you!</h2>
        <p>Your message from {request.form['email']} has been received.</p>
        <a href="/">Back to Dashboard</a>
        """
    
    return render_template_string(CONTACT_FORM_TEMPLATE)


@app.route('/signup', methods=['GET', 'POST'])
@fv.validate({
    'form': {
        'username': {'required': True, 'rules': fv.SAFE_USERNAME},
        'email': {'required': True, 'rules': fv.EMAIL},
        'age': {'required': True, 'rules': fv.TEXT}
    }
})
def signup():
    """Protected endpoint: User signup form with validation."""
    if request.method == 'POST':
        return f"""
        <h2>Signup Successful!</h2>
        <p>Welcome, {request.form['username']}!</p>
        <a href="/">Back to Dashboard</a>
        """
    
    return render_template_string(SIGNUP_FORM_TEMPLATE)


@app.route('/api/search', methods=['POST'])
@fv.validate({
    'form': {
        'query': {'required': True, 'rules': fv.SAFE_TEXT}
    }
})
def api_search():
    """Protected endpoint: Search API that requires query validation."""
    query = request.form.get('query', '')
    return jsonify({
        'status': 'success',
        'query': query,
        'results': [f'Result for: {query}']
    })


# ============================================================================
# EXCLUDED ENDPOINTS - These intentionally skip validation
# ============================================================================

@app.route('/health')
@fv.exclude_validation("Health check endpoint - no user input")
def health_check():
    """Excluded endpoint: System health status check."""
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running normally'
    })


@app.route('/about')
@fv.exclude_validation("Static about page - no form processing")
def about_page():
    """Excluded endpoint: Static informational page."""
    return render_template_string(ABOUT_TEMPLATE)


@app.route('/api/info')
@fv.exclude_validation("Read-only endpoint - returns system info only")
def api_info():
    """Excluded endpoint: API info endpoint that returns data without validation."""
    return jsonify({
        'application': 'flask-request-validate example',
        'version': '1.0.0',
        'description': 'Demonstrates protected, excluded, and unprotected endpoints'
    })


# ============================================================================
# UNPROTECTED ENDPOINTS - Regular routes without validation
# ============================================================================

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Unprotected endpoint: Accepts any input without validation."""
    if request.method == 'POST':
        # No validation - accepts anything
        feedback_text = request.form.get('feedback', 'No feedback provided')
        return f"""
        <h2>Feedback Received</h2>
        <p>Your feedback: {feedback_text}</p>
        <a href="/">Back to Dashboard</a>
        """
    
    return render_template_string(FEEDBACK_FORM_TEMPLATE)


@app.route('/echo', methods=['POST'])
def echo():
    """Unprotected endpoint: Echo back whatever is sent (no validation)."""
    data = {key: request.form.get(key, '') for key in request.form.keys()}
    return jsonify({
        'status': 'echoed',
        'data': data
    })


@app.route('/comments', methods=['GET'])
def comments_page():
    """Unprotected endpoint: Returns a simple page."""
    return """
    <h2>Comments Page</h2>
    <p>This is an unprotected endpoint with no validation.</p>
    <a href="/">Back to Dashboard</a>
    """


# ============================================================================
# MAIN DASHBOARD - Shows report of all endpoints
# ============================================================================

@app.route('/')
@fv.exclude_validation("Dashboard endpoint - displays status report")
def dashboard():
    """Main dashboard showing status of all endpoints."""
    status = fv.get_route_security_status()
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        protected_count=status['protected_count'],
        excluded_count=status['excluded_count'],
        unprotected_count=status['unprotected_count'],
        protected_routes=status['protected'],
        excluded_routes=status['excluded'],
        unprotected_routes=status['unprotected']
    )


# ============================================================================
# HTML TEMPLATES
# ============================================================================

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask-Request-Validate Endpoint Status Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 { 
            color: #333; 
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .summary-card {
            padding: 20px;
            border-radius: 6px;
            color: white;
            text-align: center;
        }
        .summary-card h3 {
            font-size: 0.9em;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        .summary-card .count {
            font-size: 2.5em;
            font-weight: bold;
        }
        .protected { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .excluded { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .unprotected { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        
        .routes-section {
            margin-bottom: 40px;
        }
        .section-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        
        .route-list {
            display: grid;
            gap: 12px;
            margin-bottom: 20px;
        }
        .route-item {
            padding: 15px;
            border-left: 4px solid;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .route-item.protected {
            border-left-color: #667eea;
            background: #f0f4ff;
        }
        .route-item.excluded {
            border-left-color: #f5576c;
            background: #fff0f5;
        }
        .route-item.unprotected {
            border-left-color: #fee140;
            background: #fffbf0;
        }
        
        .route-method {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.85em;
            margin-right: 10px;
        }
        .method-get { background: #61affe; color: white; }
        .method-post { background: #49cc90; color: white; }
        .method-put { background: #fca130; color: white; }
        .method-delete { background: #f93e3e; color: white; }
        
        .route-path {
            font-family: 'Courier New', monospace;
            color: #333;
            font-weight: 500;
        }
        
        .test-section {
            margin-top: 40px;
            padding: 20px;
            background: #f0f4ff;
            border-radius: 6px;
            border: 2px solid #667eea;
        }
        .test-section h3 {
            color: #333;
            margin-bottom: 15px;
        }
        .test-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .test-link {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            text-align: center;
            transition: background 0.3s;
        }
        .test-link:hover {
            background: #764ba2;
        }
        .empty-message {
            color: #999;
            font-style: italic;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Flask-Request-Validate Endpoint Status Report</h1>
        <p class="subtitle">Dashboard showing protected, excluded, and unprotected endpoints</p>
        
        <!-- Summary Cards -->
        <div class="summary">
            <div class="summary-card protected">
                <h3>Protected Endpoints</h3>
                <div class="count">{{ protected_count }}</div>
                <p>Validation enforced</p>
            </div>
            <div class="summary-card excluded">
                <h3>Excluded Endpoints</h3>
                <div class="count">{{ excluded_count }}</div>
                <p>Intentionally skipped</p>
            </div>
            <div class="summary-card unprotected">
                <h3>Unprotected Endpoints</h3>
                <div class="count">{{ unprotected_count }}</div>
                <p>No validation</p>
            </div>
        </div>
        
        <!-- Protected Routes -->
        <div class="routes-section">
            <div class="section-title">🔒 Protected Endpoints (Validation Enforced)</div>
            {% if protected_routes %}
                <div class="route-list">
                    {% for route in protected_routes %}
                        <div class="route-item protected">
                            <span class="route-method method-{{ route.lower().split()[0] }}">{{ route.split()[0] }}</span>
                            <span class="route-path">{{ route.split()[1] }}</span>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty-message">No protected endpoints configured</div>
            {% endif %}
        </div>
        
        <!-- Excluded Routes -->
        <div class="routes-section">
            <div class="section-title">⏭️ Excluded Endpoints (Validation Skipped)</div>
            {% if excluded_routes %}
                <div class="route-list">
                    {% for route in excluded_routes %}
                        <div class="route-item excluded">
                            <span class="route-method method-{{ route.lower().split()[0] }}">{{ route.split()[0] }}</span>
                            <span class="route-path">{{ route.split()[1] }}</span>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty-message">No excluded endpoints configured</div>
            {% endif %}
        </div>
        
        <!-- Unprotected Routes -->
        <div class="routes-section">
            <div class="section-title">🔓 Unprotected Endpoints (No Validation)</div>
            {% if unprotected_routes %}
                <div class="route-list">
                    {% for route in unprotected_routes %}
                        <div class="route-item unprotected">
                            {% for method in route.methods %}
                                <span class="route-method method-{{ method.lower() }}">{{ method }}</span>
                            {% endfor %}
                            <span class="route-path">{{ route.endpoint }}</span>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty-message">No unprotected endpoints found</div>
            {% endif %}
        </div>
        
        <!-- Test Section -->
        <div class="test-section">
            <h3>🧪 Test the Endpoints</h3>
            <p style="margin-bottom: 15px; color: #666;">Try these endpoints to see how validation works:</p>
            <div class="test-links">
                <a href="/contact" class="test-link">Contact Form (Protected)</a>
                <a href="/signup" class="test-link">Signup Form (Protected)</a>
                <a href="/feedback" class="test-link">Feedback (Unprotected)</a>
                <a href="/about" class="test-link">About Page (Excluded)</a>
                <a href="/health" class="test-link">Health Check (Excluded)</a>
                <a href="/api/info" class="test-link">API Info (Excluded)</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

CONTACT_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Contact Form</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .form-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        h1 { color: #333; margin-bottom: 10px; }
        .info { color: #666; margin-bottom: 20px; font-size: 0.95em; }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            color: #333;
            font-weight: 500;
        }
        input, textarea { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: inherit;
        }
        textarea { resize: vertical; min-height: 100px; }
        button { 
            width: 100%;
            padding: 12px; 
            background: #667eea; 
            color: white; 
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1em;
            transition: background 0.3s;
        }
        button:hover { background: #764ba2; }
        .back-link {
            display: inline-block;
            margin-top: 15px;
            color: #667eea;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>📧 Contact Us</h1>
        <p class="info">This is a <strong>PROTECTED</strong> endpoint. All inputs are validated.</p>
        <form method="POST">
            <div class="form-group">
                <label for="name">Name:</label>
                <input type="text" name="name" id="name" required>
                <small>Letters, numbers, spaces only</small>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" name="email" id="email" required>
                <small>Must be a valid email address</small>
            </div>
            <div class="form-group">
                <label for="message">Message:</label>
                <textarea name="message" id="message" required></textarea>
                <small>Safe text only</small>
            </div>
            <button type="submit">Send Message</button>
        </form>
        <a href="/" class="back-link">← Back to Dashboard</a>
    </div>
</body>
</html>
"""

SIGNUP_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>User Signup</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .form-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        h1 { color: #333; margin-bottom: 10px; }
        .info { color: #666; margin-bottom: 20px; font-size: 0.95em; }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            color: #333;
            font-weight: 500;
        }
        input { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: inherit;
        }
        button { 
            width: 100%;
            padding: 12px; 
            background: #667eea; 
            color: white; 
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1em;
            transition: background 0.3s;
        }
        button:hover { background: #764ba2; }
        .back-link {
            display: inline-block;
            margin-top: 15px;
            color: #667eea;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>👤 User Signup</h1>
        <p class="info">This is a <strong>PROTECTED</strong> endpoint. All inputs are validated.</p>
        <form method="POST">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" name="username" id="username" required>
                <small>6-20 characters, alphanumeric and underscore only</small>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" name="email" id="email" required>
                <small>Must be a valid email address</small>
            </div>
            <div class="form-group">
                <label for="age">Age:</label>
                <input type="number" name="age" id="age" required min="0" max="150">
                <small>Must be a valid integer</small>
            </div>
            <button type="submit">Create Account</button>
        </form>
        <a href="/" class="back-link">← Back to Dashboard</a>
    </div>
</body>
</html>
"""

FEEDBACK_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Feedback</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .form-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        h1 { color: #333; margin-bottom: 10px; }
        .info { color: #666; margin-bottom: 20px; font-size: 0.95em; }
        .warning { 
            background: #fff3cd; 
            border: 1px solid #ffc107;
            color: #856404;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            color: #333;
            font-weight: 500;
        }
        textarea { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: inherit;
            min-height: 100px;
            resize: vertical;
        }
        button { 
            width: 100%;
            padding: 12px; 
            background: #fa709a; 
            color: white; 
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1em;
            transition: background 0.3s;
        }
        button:hover { background: #f5576c; }
        .back-link {
            display: inline-block;
            margin-top: 15px;
            color: #fa709a;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>💬 Feedback Form</h1>
        <p class="info">This is an <strong>UNPROTECTED</strong> endpoint. No validation is enforced.</p>
        <div class="warning">
            <strong>⚠️ Warning:</strong> This endpoint accepts any input without validation. 
            Try submitting invalid data to see the difference from protected endpoints!
        </div>
        <form method="POST">
            <div class="form-group">
                <label for="feedback">Your Feedback:</label>
                <textarea name="feedback" id="feedback"></textarea>
                <small>No validation - type anything!</small>
            </div>
            <button type="submit">Submit Feedback</button>
        </form>
        <a href="/" class="back-link">← Back to Dashboard</a>
    </div>
</body>
</html>
"""

ABOUT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>About</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 { color: #333; margin-bottom: 20px; }
        .info-box {
            background: #f0f4ff;
            border-left: 4px solid #f5576c;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        p { color: #666; margin-bottom: 15px; line-height: 1.6; }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #f5576c;
            text-decoration: none;
            font-weight: 500;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ℹ️ About This Application</h1>
        
        <div class="info-box">
            <strong>This page is an EXCLUDED endpoint</strong> - It's safe to exclude because it doesn't process user input.
        </div>
        
        <h2>What is Flask-Request-Validate?</h2>
        <p>
            Flask-Request-Validate is a Python library that provides easy-to-use decorators for validating 
            incoming HTTP requests in Flask applications. It helps protect your application from 
            invalid or malicious input.
        </p>
        
        <h2>Endpoint Categories</h2>
        <p>
            This example application demonstrates three types of endpoints:
        </p>
        <ul style="margin-left: 20px;">
            <li><strong>Protected:</strong> Use @validate decorator to enforce input validation</li>
            <li><strong>Excluded:</strong> Use @exclude_validation for read-only endpoints</li>
            <li><strong>Unprotected:</strong> Regular routes without any validation</li>
        </ul>
        
        <p>
            Understanding when to use each category helps you build secure and efficient Flask applications.
        </p>
        
        <a href="/" class="back-link">← Back to Dashboard</a>
    </div>
</body>
</html>
"""


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║        Flask-Request-Validate Endpoint Status Example         ║
    ║                                                                ║
    ║  This application demonstrates:                              ║
    ║  • Protected endpoints (with validation)                     ║
    ║  • Excluded endpoints (intentionally skipped)                ║
    ║  • Unprotected endpoints (no validation)                     ║
    ║                                                                ║
    ║  Open http://127.0.0.1:5000 in your browser to see          ║
    ║  the dashboard with all endpoints and their status.          ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True)
