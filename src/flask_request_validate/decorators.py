"""
decorators.py

Flask decorator interface for request validation.

This module integrates the core validation engine with Flask by:
- extracting request data
- invoking the validator
- handling error responses
- providing security monitoring for unprotected endpoints
"""

import inspect
import warnings
import re
import uuid
from functools import wraps
from flask import request, make_response, current_app, g, session

from .validator import validate_request_data
from .errors import format_error_response, add_error


# Global registry for tracking protected/unprotected routes
_route_registry = {
    'protected': set(),
    'excluded': set(),
    'unprotected': set()
}


def exclude_validation(reason="Endpoint does not require input validation"):
    """
    Decorator to explicitly exclude an endpoint from validation requirements.

    Use this for endpoints that genuinely don't accept user input, such as:
    - Health check endpoints
    - Static pages
    - API documentation endpoints
    - Authentication endpoints that handle their own validation

    :param reason: Reason for excluding validation (for documentation)
    :type reason: str
    """
    def decorator(func):
        # Mark this function as excluded from validation
        func.__validation_excluded__ = True
        func.__validation_exclude_reason__ = reason

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add to excluded registry
            endpoint = f"{request.method} {request.path}"
            _route_registry['excluded'].add(endpoint)

            return func(*args, **kwargs)

        # Mirror exclusion attributes on the returned wrapper so route inspection
        # (before any requests) can detect the exclusion.
        wrapper.__validation_excluded__ = True
        wrapper.__validation_exclude_reason__ = reason
        wrapper._flask_validate_excluded = True
        # Keep reference to original for chained decorators
        wrapper.__original_func__ = func

        return wrapper
    return decorator


def validate_request(rules, on_error=None, security_headers=None):
    """
    Flask decorator for validating incoming request data.

    This decorator is designed to work correctly when stacked with other decorators
    by preserving function metadata and performing validation early in the call chain.

    Example usage:
        @app.route('/submit', methods=['POST'])
        @other_decorator  # Runs first
        @validate({...})  # Validation runs second
        def submit_form():
            return "Success"

    :param rules: Validation rules dictionary
    :type rules: dict
    :param on_error: Optional callable that accepts the full validation result dict and returns a Flask response
    :type on_error: callable | None
    """

    def decorator(func):
        # Store reference to original function for inspection if needed
        original_func = func

        # Mark this function as protected
        func.__validation_protected__ = True
        func.__validation_rules__ = rules

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add to protected registry
            endpoint = f"{request.method} {request.path}"
            _route_registry['protected'].add(endpoint)

            # Extract request data - do this early before other decorators can modify
            request_data = {
                "form": request.form,
                "query_string": request.args,
                "cookie": request.cookies,
                "header": request.headers,
                "method": request.method,
            }

            try:
                # If auto-CSRF is enabled, validate CSRF token for form submissions
                try:
                    auto_csrf = current_app.config.get('FLASK_VALIDATE_AUTO_CSRF', AUTO_CSRF_DEFAULT)
                    # Only enforce if auto-csrf enabled and app has a secret key configured
                    if auto_csrf and getattr(current_app, 'secret_key', None):
                        content_type = (request.content_type or '').lower()
                        if request.method in ('POST', 'PUT', 'PATCH') and (
                            content_type.startswith('application/x-www-form-urlencoded')
                            or content_type.startswith('multipart/form-data')
                        ):
                            submitted = request.form.get('flask_validate_csrf_token')
                            if not submitted or not _validate_csrf_token(submitted):
                                # CSRF token missing or invalid — record as a validation error
                                result = {"valid": False, "errors": {}}
                                add_error(result, 'flask_validate_csrf_token', 'Invalid CSRF token')
                                # ensure we skip the normal validator call below and flow
                                # into the error handling path by setting result in locals()
                                # (the code later checks for existing `result`)
                                pass
                        # Remove CSRF field from the request data we pass to the validator
                        try:
                            request_data['form'] = {k: v for k, v in request.form.items() if k != 'flask_validate_csrf_token'}
                        except Exception:
                            pass
                except Exception:
                    # don't break normal flow on failures in CSRF helper
                    pass

                # Run validation (unless CSRF already produced a `result`)
                if 'result' not in locals():
                    result = validate_request_data(rules, request_data)

                if not result["valid"]:
                    # Build error response and apply security headers
                    if on_error:
                        response = make_response(on_error(result))
                    else:
                        html = format_error_response(result)
                        response = make_response(html)
                        response.status_code = 400

                    # Compute header settings and apply
                    header_settings = _build_security_header_settings(current_app.config)
                    if security_headers:
                        header_settings = _merge_settings(header_settings, security_headers)
                    _apply_security_headers(response, header_settings)

                    return response

                # Call the original function
                returned = func(*args, **kwargs)

                # Wrap into a Flask response so we can attach headers
                response = make_response(returned)

                # Compute header settings and apply
                header_settings = _build_security_header_settings(current_app.config)
                if security_headers:
                    header_settings = _merge_settings(header_settings, security_headers)
                _apply_security_headers(response, header_settings)

                return response

            except Exception as e:
                # Re-raise exceptions to maintain normal error handling
                # This ensures other decorators can still handle exceptions properly
                raise

        # Store original function on wrapper for inspection by other decorators
        wrapper.__original_func__ = original_func
        wrapper.__validation_rules__ = rules
        # Mark wrapper as protected for external checks and backward compatibility
        wrapper._flask_validate_protected = True
        # Keep static per-decorator security overrides accessible
        wrapper.__security_headers__ = security_headers

        return wrapper

    return decorator


# Module-level defaults for security headers. Exported so callers can mutate
# them at runtime if they prefer global changes instead of app.config.
SECURITY_HEADER_DEFAULTS = {
    'Content-Security-Policy': {
        'enabled': True,
        'value': "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    },
    'X-Frame-Options': {
        'enabled': True,
        'value': 'DENY'
    },
    'X-Content-Type-Options': {
        'enabled': True,
        'value': 'nosniff'
    },
    'Referrer-Policy': {
        'enabled': True,
        'value': 'no-referrer'
    },
    'Permissions-Policy': {
        'enabled': True,
        'value': 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=()'
    },
    'Strict-Transport-Security': {
        'enabled': True,
        'value': 'max-age=63072000; includeSubDomains; preload'
    }
}

# Module-level default for auto CSRF behavior. Exported so callers can
# disable globally before app creation (e.g. `fv.AUTO_CSRF_DEFAULT = False`).
# Enabled by default to provide safer defaults.
AUTO_CSRF_DEFAULT = True


def _build_security_header_settings(app_config, app_key='FLASK_VALIDATE_SECURITY_HEADERS'):
    # copy the module-level defaults to avoid accidental mutation
    defaults = {k: v.copy() for k, v in SECURITY_HEADER_DEFAULTS.items()}
    try:
        cfg = app_config.get(app_key, None)
    except Exception:
        cfg = None

    if not cfg or not isinstance(cfg, dict):
        return defaults

    return _merge_settings(defaults, cfg)


def _merge_settings(base, override):
    if not override:
        return base
    merged = {k: v.copy() for k, v in base.items()}
    for h, opts in override.items():
        if h not in merged:
            if isinstance(opts, dict):
                merged[h] = {
                    'enabled': bool(opts.get('enabled', True)),
                    'value': opts.get('value', '')
                }
            else:
                merged[h] = {'enabled': True, 'value': str(opts)}
        else:
            if isinstance(opts, dict):
                if 'enabled' in opts:
                    merged[h]['enabled'] = bool(opts['enabled'])
                if 'value' in opts:
                    merged[h]['value'] = opts['value']
            else:
                merged[h]['value'] = str(opts)

    return merged


def _apply_security_headers(response, header_settings):
    if not header_settings:
        return
    # Remove any Server header to avoid leaking server information
    try:
        if 'Server' in response.headers:
            del response.headers['Server']
    except Exception:
        pass
    for header, opts in header_settings.items():
        try:
            if not opts.get('enabled', True):
                if header in response.headers:
                    del response.headers[header]
                continue
            value = opts.get('value', '')
            if value:
                response.headers[header] = value
        except Exception:
            continue


def _generate_csrf_token():
    """Generate a new CSRF token string."""
    return uuid.uuid4().hex


def _store_csrf_token_in_session(token):
    """Store the token in session under a random session key.

    We purposefully use a random session key name so attackers cannot
    predict the session structure; inbound validation will search
    session values for a matching token.
    """
    try:
        key = 'fv_csrf_' + uuid.uuid4().hex
        session[key] = token
        return True
    except Exception:
        return False


def _validate_csrf_token(submitted_token):
    """Validate the submitted token against session-stored tokens.

    If found, consume it (delete from session) and return True.
    """
    try:
        # Linear search through session values for matching token
        keys_to_remove = []
        for k, v in list(session.items()):
            try:
                if v == submitted_token and k.startswith('fv_csrf_'):
                    keys_to_remove.append(k)
            except Exception:
                continue
        for k in keys_to_remove:
            try:
                del session[k]
            except Exception:
                pass
        return len(keys_to_remove) > 0
    except Exception:
        return False


def init_app(app):
    """Initialize Flask app integration.

    Registers an `after_request` handler that applies security headers to
    every outgoing response. Per-route overrides are respected when a view
    function exposes a `__security_headers__` attribute (set by using the
    `security_headers` parameter on `@fv.validate(...)`).
    """

    # Prevent double-initialization
    if getattr(app, 'extensions', None) is None:
        app.extensions = {}
    if app.extensions.get('flask_validate_security'):
        return
    app.extensions['flask_validate_security'] = True

    # Wrap the app.wsgi_app with middleware that strips the Server header
    class _ServerHeaderStripperMiddleware:
        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app

        def __call__(self, environ, start_response):
            def _start_response(status, response_headers, exc_info=None):
                try:
                    # Filter out any Server header (case-insensitive)
                    filtered = [(k, v) for (k, v) in response_headers if k.lower() != 'server']
                except Exception:
                    filtered = response_headers
                return start_response(status, filtered, exc_info)

            return self.wsgi_app(environ, _start_response)

    try:
        # Avoid double-wrapping
        if not isinstance(getattr(app, 'wsgi_app', None), _ServerHeaderStripperMiddleware):
            app.wsgi_app = _ServerHeaderStripperMiddleware(app.wsgi_app)
    except Exception:
        pass
    # Attempt to silence Werkzeug's default Server header by overriding
    # the request handler's version_string method when Werkzeug is present.
    try:
        import werkzeug.serving as _ws

        def _empty_version_string(self):
            return ''

        # Monkeypatch the handler to avoid emitting Server header
        if hasattr(_ws, 'WSGIRequestHandler'):
            try:
                _ws.WSGIRequestHandler.version_string = _empty_version_string
            except Exception:
                pass
    except Exception:
        pass

    @app.after_request
    def _apply_headers_middleware(response):
        try:
            # Base settings from app config
            header_settings = _build_security_header_settings(app.config)

            # Attempt to detect per-route overrides
            try:
                endpoint = getattr(request, 'endpoint', None)
                if endpoint:
                    view_func = app.view_functions.get(endpoint)
                    # If wrapped, prefer attribute on wrapper
                    if view_func is not None:
                        # If wrapper exposes __security_headers__, use it
                        per = getattr(view_func, '__security_headers__', None)
                        if per:
                            header_settings = _merge_settings(header_settings, per)
                        else:
                            # try original function chain
                            f = view_func
                            seen = set()
                            while hasattr(f, '__original_func__') and id(f) not in seen:
                                seen.add(id(f))
                                f = getattr(f, '__original_func__')
                                per = getattr(f, '__security_headers__', None)
                                if per:
                                    header_settings = _merge_settings(header_settings, per)
                                    break
            except Exception:
                pass

            _apply_security_headers(response, header_settings)

            # Inject CSRF tokens into HTML forms for GET/HTML responses.
            try:
                # Only operate on HTML responses and if auto-CSRF is enabled and app has secret_key
                auto_csrf = app.config.get('FLASK_VALIDATE_AUTO_CSRF', AUTO_CSRF_DEFAULT)
                if not (auto_csrf and getattr(app, 'secret_key', None)):
                    pass
                else:
                    ctype = (response.content_type or '').lower()
                    # Inject into any HTML response regardless of status code so
                    # clients receive security headers and CSRF tokens even on
                    # error pages or redirects that render HTML.
                    if 'html' in ctype:
                        try:
                            text = response.get_data(as_text=True)
                        except Exception:
                            text = ''
                        # Quick check for any forms
                        if text and '</form' in text.lower():
                            # Generate token and store in session
                            token = _generate_csrf_token()
                            _store_csrf_token_in_session(token)

                            # Hidden input to inject
                            hidden = f'<input type="hidden" name="flask_validate_csrf_token" value="{token}" />'

                            # Insert hidden input before each closing form tag
                            try:
                                new_text = re.sub(r'</form\s*>', hidden + '</form>', text, flags=re.IGNORECASE)
                                response.set_data(new_text)
                            except Exception:
                                # fallback: do nothing if replacement fails
                                pass
            except Exception:
                # never break response flow due to CSRF injection errors
                pass
        except Exception:
            # never break response flow
            pass
        return response


# By default, enable security headers for all Flask apps created after
# this module is imported. We patch Flask.__init__ to call `init_app`
# during app construction so users get secure headers without calling
# `fv.init_app(app)` explicitly. This is safe because `init_app` is
# idempotent and will not register handlers multiple times.
try:
    from flask import Flask
    _original_flask_init = Flask.__init__

    def _flask_init_and_register(self, *args, **kwargs):
        _original_flask_init(self, *args, **kwargs)
        try:
            init_app(self)
        except Exception:
            # Don't break app creation if something goes wrong
            pass

    Flask.__init__ = _flask_init_and_register
except Exception:
    # If Flask isn't available at import time, skip auto-init. It will
    # still work if the user calls `fv.init_app(app)` manually.
    pass


def check_unprotected_routes(app=None, warn_unprotected=True, fail_on_unprotected=False):
    """
    Check for unprotected Flask routes that may accept user input.

    This function scans all registered routes and identifies those that:
    - Accept POST/PUT/PATCH methods (likely to receive user input)
    - Are not decorated with @validate or @exclude_validation

    :param app: Flask app instance (uses current_app if None)
    :param warn_unprotected: Whether to emit warnings for unprotected routes
    :param fail_on_unprotected: Whether to raise an exception for unprotected routes
    :return: Dict with protected, excluded, and unprotected routes
    :raises: RuntimeError if fail_on_unprotected=True and unprotected routes found
    """
    if app is None:
        app = current_app

    # Detect whether app has a secret_key configured (required for server-side sessions)
    try:
        secret_key_set = bool(getattr(app, 'secret_key', None))
    except Exception:
        secret_key_set = False

    unprotected_routes = []
    protected_list = []
    excluded_list = []

    def _resolve_original(f):
        # Walk any wrapper chain to the original function, if present
        seen = set()
        while hasattr(f, '__original_func__') and id(f) not in seen:
            seen.add(id(f))
            f = getattr(f, '__original_func__')
        return f

    with app.app_context():
        for rule in app.url_map.iter_rules():
            # Skip static routes and HEAD/OPTIONS methods
            if rule.endpoint == 'static' or rule.rule == '/static/<path:filename>':
                continue

            for method in rule.methods:
                if method in ('HEAD', 'OPTIONS'):
                    continue

                endpoint = f"{method} {rule.rule}"

                # Prefer explicit runtime registry entries if present
                if endpoint in _route_registry['protected']:
                    protected_list.append(endpoint)
                    continue
                if endpoint in _route_registry['excluded']:
                    excluded_list.append(endpoint)
                    continue

                # Inspect the Flask view function for decorator-set attributes
                view_func = app.view_functions.get(rule.endpoint)
                resolved = _resolve_original(view_func) if view_func else None

                is_protected = False
                is_excluded = False

                if view_func is not None:
                    if getattr(view_func, '_flask_validate_protected', False) or getattr(view_func, '__validation_protected__', False):
                        is_protected = True
                    if getattr(view_func, '_flask_validate_excluded', False) or getattr(view_func, '__validation_excluded__', False):
                        is_excluded = True

                if not (is_protected or is_excluded) and resolved is not None and resolved is not view_func:
                    # Check attributes on resolved/original function as well
                    if getattr(resolved, '_flask_validate_protected', False) or getattr(resolved, '__validation_protected__', False):
                        is_protected = True
                    if getattr(resolved, '_flask_validate_excluded', False) or getattr(resolved, '__validation_excluded__', False):
                        is_excluded = True

                if is_protected:
                    protected_list.append(endpoint)
                    continue
                if is_excluded:
                    excluded_list.append(endpoint)
                    continue

                # Consider routes that accept user input as potentially unprotected
                if method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                    # POST/PUT/PATCH/DELETE routes are more likely to accept user input
                    unprotected_routes.append({
                        'endpoint': endpoint,
                        'method': method,
                        'rule': rule.rule,
                        'likely_input_route': True
                    })
                elif method == 'GET' and '<' in rule.rule:
                    # GET routes with parameters might need validation
                    unprotected_routes.append({
                        'endpoint': endpoint,
                        'method': method,
                        'rule': rule.rule,
                        'likely_input_route': True
                    })
                elif method == 'GET':
                    # GET routes without parameters are less likely to need validation, but still track them
                    unprotected_routes.append({
                        'endpoint': endpoint,
                        'method': method,
                        'rule': rule.rule,
                        'likely_input_route': False
                    })

    if unprotected_routes and warn_unprotected:
        warnings.warn(
            f"Found {len(unprotected_routes)} potentially unprotected routes that may accept user input:\n" +
            "\n".join([f"  - {route['endpoint']}" for route in unprotected_routes]) +
            "\n\nConsider adding @validate() decorators or @exclude_validation() for routes that don't need validation.",
            UserWarning,
            stacklevel=2
        )

    # Warn when secret_key is not set since sessions (and CSRF tokens) won't work
    if not secret_key_set and warn_unprotected:
        warnings.warn(
            "Flask app has no `secret_key` configured; server-side sessions are disabled. "
            "CSRF token injection/validation will not function without sessions. Set `app.secret_key` or configure a session backend.",
            UserWarning,
            stacklevel=2
        )

    if unprotected_routes and fail_on_unprotected:
        raise RuntimeError(
            f"Found {len(unprotected_routes)} unprotected routes. "
            "Add @validate() decorators or @exclude_validation() decorators as appropriate."
        )
    
    return {
        'protected': sorted(protected_list),
        'excluded': sorted(excluded_list),
        'unprotected': sorted(unprotected_routes, key=lambda r: r['endpoint']),
        'secret_key_set': secret_key_set
    }


def get_route_security_status():
    """
    Get the current security status of all registered routes.

    :return: Dict with route security information
    """
    # Build an accurate status by scanning the app routes via check_unprotected_routes
    try:
        result = check_unprotected_routes(warn_unprotected=False)
    except TypeError:
        # Older call-sites may not pass app; ensure current_app is used by check_unprotected_routes
        result = check_unprotected_routes(None, warn_unprotected=False)

    return {
        'protected_count': len(result.get('protected', [])),
        'excluded_count': len(result.get('excluded', [])),
        'unprotected_count': len(result.get('unprotected', [])),
        'protected': result.get('protected', []),
        'excluded': result.get('excluded', []),
        'unprotected': result.get('unprotected', []),
        'secret_key_set': result.get('secret_key_set', False)
    }