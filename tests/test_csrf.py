import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import re
import flask_request_validate as fv
from minimal_app import app


def _extract_csrf_token_from_html(html):
    m = re.search(r'name="flask_request_validate_csrf_token"\s+value="([0-9a-f]+)"', html)
    return m.group(1) if m else None


def test_csrf_injection_and_session_storage():
    # enable auto-CSRF and set secret key for sessions; restore after test
    orig_auto = app.config.get('FLASK_REQUEST_VALIDATE_AUTO_CSRF', False)
    orig_secret = getattr(app, 'secret_key', None)
    try:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = True
        app.secret_key = 'test-secret'

        client = app.test_client()

        # GET should inject hidden input and store token in session
        r = client.get('/')
        assert r.status_code == 200
        text = r.get_data(as_text=True)
        token = _extract_csrf_token_from_html(text)
        assert token is not None

        # session should contain a stored token matching the injected token
        found = False
        with client.session_transaction() as sess:
            for k, v in sess.items():
                if k.startswith('fv_csrf_') and v == token:
                    found = True
                    break
        assert found
    finally:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = orig_auto
        app.secret_key = orig_secret


def test_csrf_validation_consumes_token_on_post():
    orig_auto = app.config.get('FLASK_REQUEST_VALIDATE_AUTO_CSRF', False)
    orig_secret = getattr(app, 'secret_key', None)
    try:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = True
        app.secret_key = 'test-secret'
        client = app.test_client()

        # Obtain a fresh token via GET
        r = client.get('/')
        text = r.get_data(as_text=True)
        token = _extract_csrf_token_from_html(text)
        assert token is not None

        # POST with token should succeed
        r2 = client.post('/', data={'name': 'alice', 'flask_request_validate_csrf_token': token})
        if r2.status_code != 200:
            body = r2.get_data(as_text=True)
            with client.session_transaction() as s:
                sess_items = dict(s)
            raise AssertionError(f"POST failed status={r2.status_code}; body={body!r}; session={sess_items}")

        # Reuse of same token should fail (token consumed)
        r3 = client.post('/', data={'name': 'alice', 'flask_request_validate_csrf_token': token})
        assert r3.status_code == 400
    finally:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = orig_auto
        app.secret_key = orig_secret


def test_csrf_missing_token_rejected():
    orig_auto = app.config.get('FLASK_REQUEST_VALIDATE_AUTO_CSRF', False)
    orig_secret = getattr(app, 'secret_key', None)
    try:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = True
        app.secret_key = 'test-secret'
        client = app.test_client()

        # POST without token should be rejected
        r = client.post('/', data={'name': 'alice'})
        assert r.status_code == 400
        body = r.get_data(as_text=True)
        assert 'Invalid CSRF token' in body or 'flask_request_validate_csrf_token' in body
    finally:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = orig_auto
        app.secret_key = orig_secret


def test_csrf_mismatched_token_rejected():
    orig_auto = app.config.get('FLASK_REQUEST_VALIDATE_AUTO_CSRF', False)
    orig_secret = getattr(app, 'secret_key', None)
    try:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = True
        app.secret_key = 'test-secret'
        client = app.test_client()

        # Get a valid token, then submit a modified (mismatched) token
        r = client.get('/')
        text = r.get_data(as_text=True)
        token = _extract_csrf_token_from_html(text)
        assert token is not None

        bad = token[:-1] + ('0' if token[-1] != '0' else '1')
        r2 = client.post('/', data={'name': 'alice', 'flask_request_validate_csrf_token': bad})
        assert r2.status_code == 400
        body = r2.get_data(as_text=True)
        assert 'Invalid CSRF token' in body or 'flask_request_validate_csrf_token' in body
    finally:
        app.config['FLASK_REQUEST_VALIDATE_AUTO_CSRF'] = orig_auto
        app.secret_key = orig_secret
