# API Reference

This is a brief reference for the top-level API exported by `flask_request_validate`.

- `fv.validate(rules, on_error=None)` — decorator to validate incoming request data. `on_error` is an optional callable that receives the full validation `result` dict and must return a Flask response.
- `fv.exclude_validation(reason)` — mark an endpoint as excluded from validation.
- `fv.check_unprotected_routes(app=None, warn_unprotected=True, fail_on_unprotected=False)` — scan Flask app for routes that are likely to accept input but lack validation.
- `fv.get_route_security_status()` — return counts and lists for protected/excluded/unprotected routes.

Validation result structure (returned to `on_error` handlers):

```
{
  'valid': False,
  'errors': {
      'email': ['Missing form data: email'],
      'age': ['age must be a whole number']
  },
  '_error_sequence': [('email','Missing form data: email'), ('age','age must be a whole number')]
}
```

Notes:

- Handlers should read `result['errors']` for programmatic behavior. The `_error_sequence` field is used internally to preserve ordering for the default HTML formatter.
- Do not rely on `_error_sequence` for stable API; prefer `errors` dict.
