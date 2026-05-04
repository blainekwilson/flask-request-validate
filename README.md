# 🚀 flask-validate

**Lightweight, decorator-based input validation for Flask apps**

---

## 🚧 Pre-release Feedback Wanted

I'm looking for feedback before publishing to PyPI:

👉 https://github.com/blainekwilson/flask-validate/discussions

Would especially appreciate input on API design and validation patterns.

---

## 🎯 Why this exists

If you are building Flask apps, there are established frameworks you should consider first.

* 🧱 Server-side rendered HTML apps → use Flask-WTF
* 🔌 REST APIs → use Marshmallow or Pydantic


👉 In practice, a large number of Flask applications still don’t use a structured validation framework and rely on ad hoc validation instead.

👉 flask-validate exists to provide a lightweight, auditable alternative for those cases.

---

## ✨ What makes this different

- ✅ Decorator-based validation — no forms, no schemas  
- ✅ Works with query strings + form data  
- ✅ Field-level error handling  
- ✅ Custom error responses (HTML, JSON, anything)  
- 🔥 Security audit tool to detect unprotected routes  

---

## ⚡ Quick example

```python
from flask import Flask, request
import flask_validate as fv

app = Flask(__name__)

@app.route("/submit", methods=["POST"])
@fv.validate({
    "args": {
        "st": {"required": True, "rules": fv.US_STATE}
    },
    "form": {
        "zip": {"required": False, "rules": fv.US_ZIP}
    }
})
def submit():
    return f"State: {request.args['st']}"
```

---

## 🧠 Error handling (simple → advanced)

### Default (HTML response)

```python
@fv.validate(schema)
def route():
    ...
```

### Custom error handler (recommended)

```python
def json_error_handler(result):
    return {"errors": result["errors"]}, 400

@fv.validate(schema, on_error=json_error_handler)
def route():
    ...
```

### Field-level errors

```json
{
  "errors": {
    "zip": ["Invalid ZIP code"],
    "st": ["Invalid US state"]
  }
}
```

---

## 🔐 Built-in Security Audit

Find routes that accept input **without validation**.

### Run it:

```bash
python -m audit_security app:app
```

### What it detects

- ✅ Routes protected with @validate  
- ⚪ Routes explicitly excluded  
- ❌ Routes missing validation (potential risk)  

### Example output

```
🔍 Flask Validate Security Audit Report
==================================================
📊 OVERALL SUMMARY:
   Total routes analyzed: 42
   ✅ Protected routes: 38
   ⚪ Excluded routes: 2
   ❌ Unprotected routes: 2
   🔒 Security Score: 95.2%

❌ UNPROTECTED ROUTES:
   🚨 POST /api/admin (high priority)
   ℹ️  GET / (low priority)
```

---

## 🧩 When to use this

Use flask-validate when:

- You want simple, explicit validation and you aren't using an existing framework 

---

## 🚫 When NOT to use this

- UI apps → use Flask-WTF  
- API-first apps → use Pydantic or Marshmallow  

---

## 📦 Installation (development)

```bash
pip install -e .
```

Planned: PyPI release as flask-validate

---

## 🛡️ Security-first design

- Inspired by OWASP validation guidance  
- Built to reduce common input validation mistakes  
- Includes runtime auditing for missing protections  

## 🔐 Security Response Headers (enabled by default)

flask-validate now applies several security HTTP response headers by default to every Flask response:
How it works

- Headers applied: `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, and `Strict-Transport-Security` (configurable).

How to customize

- **Global defaults** (process-wide): mutate `fv.SECURITY_HEADER_DEFAULTS` before creating your `Flask` app.
- **Per-app override**: set `app.config['FLASK_VALIDATE_SECURITY_HEADERS']` to a dict of header overrides before running the app.
- **Per-route override**: pass `security_headers` to the `@fv.validate(..., security_headers=...)` decorator for route-level control.

Server header stripping

- The package attempts to remove/blank the `Server` header to avoid leaking server/version information. It installs WSGI middleware that filters `Server` from response headers and also monkeypatches Werkzeug's handler version string when possible.
- Note: some development servers may still emit an empty `Server:` header; removing the header entirely is best handled at the HTTP server/proxy layer (nginx/Gunicorn, etc.).

Auto-initialization and `init_app`

- By default `flask_validate.init_app(app)` is called automatically for every `Flask` app created after the module is imported (we monkeypatch `Flask.__init__` to call `init_app`). You can still call `fv.init_app(app)` explicitly — it is idempotent.
- `init_app` wraps `app.wsgi_app` with the Server-header-stripping middleware and registers the `after_request` hook that applies headers and (optionally) injects CSRF tokens.

Exports

- `fv.SECURITY_HEADER_DEFAULTS`: module-level dict of header defaults (exported so callers can mutate before app creation).

Tests and examples

- Test coverage for headers is in `tests/test_security_headers.py`.
- Examples: `examples/sample_login.py` (now demonstrates CSRF injection), `examples/example_override_header.py`.


## Automatic CSRF injection and validation

- **Default**: Automatic CSRF injection/validation is enabled by default via `fv.AUTO_CSRF_DEFAULT = True`.

    - Disable globally before creating apps: set `fv.AUTO_CSRF_DEFAULT = False`.
    - Disable per-app: `app.config['FLASK_VALIDATE_AUTO_CSRF'] = False`.

- **Sessions required**: You must set `app.secret_key` (or configure a session backend) for server-side token storage. The library only injects/enforces CSRF when a session secret is available.

```python
app.secret_key = 'a-secure-secret'
```

What it does when enabled

- Injects a hidden input named `flask_validate_csrf_token` into any HTML response that contains `</form>`.
- Stores a server-side token in the user's session using a randomized session key (prefixed with `fv_csrf_`). Tokens are single-use and consumed on successful validation.
- For inbound form submissions (`application/x-www-form-urlencoded` or `multipart/form-data`) on routes decorated with `@fv.validate(...)`, the decorator will validate the submitted token against session-stored tokens.

Notes & guidance

- Tokens are single-use and stored under randomized session keys to avoid predictable session layout.
- If you prefer custom behavior (different field name, TTL, persistent tokens), disable `AUTO_CSRF_DEFAULT` and implement your own lifecycle.

Check-unprotected-routes secret-key detection

- `fv.check_unprotected_routes(app)` now detects whether `app.secret_key` is set and will emit a warning if sessions are not configured (CSRF injection/validation will not function). The returned status dict includes the boolean key `secret_key_set`.


---

## 🧭 Roadmap
- [x] form field validation
- [x] query string validation
- [x] audit for unprotected endpoints
- [x] throw error if additional fields found
- [x] support error function callback and HTML output
- [x] CSRF Token Support (by default)
- [x] Security Response Headers (by default)
- [ ] PyPI release  
- [ ] Authentication and Authorization  
- [ ] Custom rule extensions  
- [ ] Enhanced reporting + CLI options  
---

## 🤝 Contributing


---

## ⭐ Why this project stands out

Most validation libraries focus on:

- full frameworks  
- API schemas  

This one focuses on Flask applications with no validation frameworks.

And adds something most don’t:

> 🔥 Runtime detection of missing validation (security auditing)
