import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import flask_request_validate as fv
from examples import sample_registration_app as s


def test_default_security_headers_present():
    """Ensure default security headers are present on example app responses."""
    app = s.app
    # disable HSTS for local HTTP example/testing
    app.config['FLASK_VALIDATE_SECURITY_HEADERS'] = {
        'Strict-Transport-Security': {'enabled': False}
    }

    client = app.test_client()
    r = client.get('/')
    assert r.status_code == 200

    # Server header should be removed or empty
    assert r.headers.get('Server', '') == ''

    # Determine expected headers by merging defaults with app.config in-test
    app_cfg = app.config.get('FLASK_VALIDATE_SECURITY_HEADERS', {}) or {}
    for header, opts in fv.SECURITY_HEADER_DEFAULTS.items():
        # app_cfg may contain per-header dicts overriding enabled/value
        overridden = app_cfg.get(header)
        if isinstance(overridden, dict) and 'enabled' in overridden:
            enabled = bool(overridden['enabled'])
        else:
            enabled = bool(opts.get('enabled', True))

        if enabled:
            # If enabled, verify header present and equals effective value (prefer app override value)
            expected_value = opts.get('value')
            if isinstance(overridden, dict) and 'value' in overridden:
                expected_value = overridden['value']
            assert header in r.headers
            assert r.headers[header] == expected_value
        else:
            assert header not in r.headers


def test_override_default_before_app_creation(monkeypatch):
    """Mutate `SECURITY_HEADER_DEFAULTS` before app creation and confirm value is used."""
    # pick a header to override
    hdr = 'Referrer-Policy'
    original = fv.SECURITY_HEADER_DEFAULTS[hdr].copy()
    try:
        fv.SECURITY_HEADER_DEFAULTS[hdr]['value'] = 'strict-origin'

        # create a fresh Flask app after mutating defaults
        from flask import Flask

        app = Flask('fv_test_override')

        @app.route('/')
        def index():
            return 'ok'

        # disable HSTS for this local HTTP test app
        app.config['FLASK_VALIDATE_SECURITY_HEADERS'] = {
            'Strict-Transport-Security': {'enabled': False}
        }

        client = app.test_client()
        r = client.get('/')
        assert r.status_code == 200
        assert r.headers.get(hdr) == 'strict-origin'
        # Server header should be removed or empty
        assert r.headers.get('Server', '') == ''

    finally:
        # restore
        fv.SECURITY_HEADER_DEFAULTS[hdr] = original
