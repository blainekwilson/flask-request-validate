"""
Integration tests for ``flask_request_validate`` against the fixture app ``sample_app.py``.

Uses Flask's test client to assert status codes and HTML error bodies. Failure
responses are HTTP 400 with ``<html><body>…</br>…`` payloads from the validator.
"""
import unittest
import os
import sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.abspath(os.path.join(_here, '..')))
sys.path.insert(0, os.path.abspath(os.path.join(_here, '..', 'src')))
from sample_app import app


class AppTestCase(unittest.TestCase):
    """End-to-end validation behavior for query args, forms, cookies, and headers."""

    def setUp(self):
        """Push an application context and build a test client."""
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        self.app = app


    def tearDown(self):
        """Pop the application context."""
        self.ctx.pop()

    def test_query_state(self):
        """Query string: US state abbreviation (``SAFE_US_STATE``).

        Validates: successful ``st`` (raw and percent-encoded), optional field
        present or omitted, missing required param, invalid code, length vs regex
        errors, and combined messages when multiple rules fail.
        """
        # required data
        # positive test
        # normal
        response = self.client.get("/get_us_state_required", query_string={"st": "FL"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'FL')
        # encoded
        response = self.client.get("/get_us_state_required?st=F%4C")
        self.assertEqual(response.get_data(as_text=True), 'FL')
        # optional
        response = self.client.get("/get_us_state_optional", query_string={"st": "FL"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'FL')

        # negative tests
        # missing
        response = self.client.get("/get_us_state_required")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('st: Missing query_string data: st', body)
        # wrong state
        response = self.client.get("/get_us_state_required", query_string={"st": "FJ"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('st: st must be a US state', body)
        # too long
        response = self.client.get("/get_us_state_required", query_string={"st": "FLL"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('st: st must be shorter than 2 characters', body)
        self.assertIn('st: st must be a US state', body)

        # optional data
        response = self.client.get("/get_us_state_optional")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'missing state')

    def test_extra_data(self):
        """Query string: undeclared keys produce an error.
        """
        # extra query string data
        response = self.client.get("/get_us_state_required", query_string={"st": "FL", "extra": "value"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('extra: Unexpected data received', body)
        # extra form data
        response = self.client.post("/post_us_state_required", data={"st": "FL", "extra": "value"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('extra: Unexpected data received', body)


    def test_form_state(self):
        """Form POST + query: US state in body and/or query string.

        Validates: required ``st`` on POST, combined POST with both ``stq`` (query)
        and ``stf`` (form), missing fields, invalid state, and error ordering when
        both query and form keys are missing.
        """
        # required data
        # positive test
        # normal
        response = self.client.post("/post_us_state_required", data={"st": "FL"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'FL')
        # query and form
        response = self.client.post("/post_with_query_us_state_required",
                                    query_string={"stq": "FL"},
                                    data={"stf": "FL"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'FLFL')

        # negative tests
        # missing
        response = self.client.post("/post_us_state_required")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('st: Missing form data: st', body)
        # wrong state
        response = self.client.post("/post_us_state_required", data={"st": "FJ"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('st: st must be a US state', body)
        # query and form
        # missing query
        response = self.client.post("/post_with_query_us_state_required",
                                    data={"stf": "FL"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('stq: Missing query_string data: stq', body)
        # missing form
        response = self.client.post("/post_with_query_us_state_required",
                                    query_string={"stq": "FL"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('stf: Missing form data: stf', body)
        # missing both
        response = self.client.post("/post_with_query_us_state_required")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('stf: Missing form data: stf', body)
        self.assertIn('stq: Missing query_string data: stq', body)


    def test_query_int(self):
        """Query string: integer with min/max bounds (type ``int``).

        Validates: in-range value, missing param, below min, above max, non-integer
        input, and rejection of undeclared query keys (``Unexpected data``).
        """
        # positive test
        response = self.client.get("/get_int", query_string={"test": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '2')

        # missing data
        response = self.client.get("/get_int")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: Missing query_string data: test', body)

        # less than minimum
        response = self.client.get("/get_int", query_string={"test": "1"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be less than 2', body)

        # greater than maximum
        response = self.client.get("/get_int", query_string={"test": "12"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be greater than 10', body)

        # not a number
        response = self.client.get("/get_int", query_string={"test": "a"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test must be a whole number', body)

        # extra data
        response = self.client.get("/get_int", query_string={"test": "2", "extra": "a"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('extra: Unexpected data received', body)


    def test_form_int(self):
        """Form POST: integer with min/max bounds (type ``int``).

        Validates: in-range value, missing field, below min, above max, and
        undeclared form fields.
        """
        # positive test
        response = self.client.post("/post_int", data={"test": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '2')

        # missing data
        response = self.client.post("/post_int")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: Missing form data: test', body)

        # less than minimum
        response = self.client.post("/post_int", data={"test": "1"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be less than 2', body)

        # greater than maximum
        response = self.client.post("/post_int", data={"test": "12"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be greater than 10', body)

        # extra data
        response = self.client.post("/post_int", data={"test": "2", "extra": "a"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('extra: Unexpected data received', body)


    def test_query_float(self):
        """Query string: float with min/max bounds (type ``float``).

        Validates: in-range value, missing param, below min, above max, and
        non-numeric input.
        """
        # positive test
        response = self.client.get("/get_float", query_string={"test": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '2')

        # missing data
        response = self.client.get("/get_float")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: Missing query_string data: test', body)

        # less than minimum
        response = self.client.get("/get_float", query_string={"test": "1.6"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be less than 2.0', body)

        # greater than maximum
        response = self.client.get("/get_float", query_string={"test": "35.6"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be greater than 35.5', body)

        # not a number
        response = self.client.get("/get_float", query_string={"test": "a"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test must be a number', body)


    def test_form_float(self):
        """Form POST: float with min/max bounds (type ``float``).

        Validates: in-range value, missing field, below min, and above max.
        """
        # positive test
        response = self.client.post("/post_float", data={"test": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '2')

        # missing data
        response = self.client.post("/post_float")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: Missing form data: test', body)

        # less than minimum
        response = self.client.post("/post_float", data={"test": "1.6"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be less than 2.0', body)

        # greater than maximum
        response = self.client.post("/post_float", data={"test": "35.6"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test cannot be greater than 35.5', body)


    def test_query_bool(self):
        """Query string: boolean strings (case-insensitive ``true`` / ``false``).

        Validates: accepted values, missing param, and non-boolean values.
        """
        # positive test
        response = self.client.get("/get_bool", query_string={"test": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'true')

        response = self.client.get("/get_bool", query_string={"test": "True"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'True')

        response = self.client.get("/get_bool", query_string={"test": "False"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'False')

        # negative test
        response = self.client.get("/get_bool")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: Missing query_string data: test', body)

        response = self.client.get("/get_bool", query_string={"test": "aaa"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test must be true or false', body)


    def test_form_bool(self):
        """Form POST: boolean strings (``true`` / ``false``).

        Validates: accepted values, missing field, and invalid strings.
        """
        # positive test
        response = self.client.post("/post_bool", data={"test": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'true')

        response = self.client.post("/post_bool", data={"test": "True"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'True')

        response = self.client.post("/post_bool", data={"test": "False"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'False')

        # negative test
        response = self.client.post("/post_bool")
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: Missing form data: test', body)

        response = self.client.post("/post_bool", data={"test": "aaa"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: test must be true or false', body)


    def test_username(self):
        """Form POST: ``SAFE_USERNAME`` length and alphanumeric regex.

        Validates: default min/max (6–20), ``set_min_max`` overrides (5–8), and
        too-short / too-long usernames with the expected error messages.
        """
        # positive test
        response = self.client.post("/post_user", data={"username": "blaine"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'blaine')
        response = self.client.post("/post_different_user", data={"username": "blaine"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True),'blaine')

        # negative test
        response = self.client.post("/post_user", data={"username": "blaineblaineblaineblaine"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('username: username must be shorter than 20 characters', body)
        response = self.client.post("/post_user", data={"username": "b"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('username: username must be longer than 6 characters', body)

        response = self.client.post("/post_different_user", data={"username": "b"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('username: username must be longer than 5 characters', body)


    def test_safetext(self):
        """Form POST: ``SAFE_TEXT`` with custom min length via ``set_min_max``.

        Validates: safe plain text passes; HTML/script-like input fails the
        allowed-character rule.
        """
        # positive test
        response = self.client.post("/post_text", data={"text": "This is my message."})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True),
                         'This is my message.')

        # negative test
        response = self.client.post("/post_text", data={"text": "<script>alert('here')</script>"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('text: text must be letters and spaces', body)


    def test_cookie(self):
        """Cookies: validated ``Acc-Sec`` cookie using ``SAFE_TEXT``-based rules.

        Validates: acceptable cookie value echoes OK; disallowed characters
        produce a validation error (same message style as safe text).
        """
        self.client.set_cookie('Acc-Sec', 'ABCDE')
        response = self.client.get('/get_cookie')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True),
                         'ABCDE')

        self.client.set_cookie('Acc-Sec', '<script>')
        response = self.client.get('/get_cookie')
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('Acc-Sec: Acc-Sec must be letters and spaces', body)

    def test_header(self):
        """Headers: required ``Acc-Sec`` header with ``SAFE_TEXT``-based rules.

        Validates: valid header echoes OK, missing header fails, bad characters
        fail, and undeclared query parameters are rejected (strict query match on
        routes that only declare headers).
        """
        response = self.client.get('/get_header', headers={'Acc-Sec': 'ABCDE'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True),
                         'ABCDE')

        response = self.client.get('/get_header')
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('Acc-Sec: Missing header data: Acc-Sec', body)

        response = self.client.get('/get_header', headers={'Acc-Sec': '<script>'})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('Acc-Sec: Acc-Sec must be letters and spaces', body)

        response = self.client.get('/get_header',
                                   headers={'Acc-Sec': 'ABCDE'},
                                   query_string={"test": "2"})
        self.assertEqual(response.status_code, 400)
        body = response.get_data(as_text=True)
        self.assertIn('test: Unexpected data received', body)

    def test_email(self):
        """Form POST: ``EMAIL`` pattern validation."""
        # Positive test
        response = self.client.post("/post_email", data={"email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'test@example.com')

        # Negative tests
        response = self.client.post("/post_email", data={"email": "invalid-email"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email address", response.get_data(as_text=True))

        response = self.client.post("/post_email", data={"email": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email address", response.get_data(as_text=True))

    def test_url(self):
        """Form POST: ``URL`` pattern validation."""
        # Positive test
        response = self.client.post("/post_url", data={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'https://example.com')

        # Negative tests
        response = self.client.post("/post_url", data={"url": "not-a-url"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid URL", response.get_data(as_text=True))

    def test_username_owasp(self):
        """Form POST: ``USERNAME`` (OWASP) pattern validation."""
        # Positive test
        response = self.client.post("/post_username_owasp", data={"username": "testuser123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'testuser123')

        # Negative tests
        response = self.client.post("/post_username_owasp", data={"username": "u"})  # too short
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid username", response.get_data(as_text=True))

        response = self.client.post("/post_username_owasp", data={"username": "user@domain"})  # invalid chars
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid username", response.get_data(as_text=True))

    def test_password_strong(self):
        """Form POST: ``PASSWORD_STRONG`` pattern validation."""
        # Positive test
        response = self.client.post("/post_password_strong", data={"password": "StrongPass123!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'StrongPass123!')

        # Negative tests
        response = self.client.post("/post_password_strong", data={"password": "weak"})  # too weak
        self.assertEqual(response.status_code, 400)
        self.assertIn("Password must meet complexity requirements", response.get_data(as_text=True))

    def test_credit_card(self):
        """Form POST: ``CREDIT_CARD`` pattern validation."""
        # Positive test
        response = self.client.post("/post_credit_card", data={"card": "4111111111111111"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '4111111111111111')

        # Negative tests
        response = self.client.post("/post_credit_card", data={"card": "123"})  # too short
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid", response.get_data(as_text=True))

        response = self.client.post("/post_credit_card", data={"card": "abcd"})  # non-numeric
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid", response.get_data(as_text=True))

    def test_us_zip(self):
        """Form POST: ``US_ZIP`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_us_zip", data={"zip": "12345"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '12345')

        response = self.client.post("/post_us_zip", data={"zip": "12345-6789"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '12345-6789')

        # Negative tests
        response = self.client.post("/post_us_zip", data={"zip": "1234"})  # too short
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid ZIP code", response.get_data(as_text=True))

        response = self.client.post("/post_us_zip", data={"zip": "123456"})  # too long
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid ZIP code", response.get_data(as_text=True))

    def test_us_phone(self):
        """Form POST: ``US_PHONE`` pattern validation."""
        # Positive test
        response = self.client.post("/post_us_phone", data={"phone": "555-123-4567"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '555-123-4567')

        # Negative tests
        response = self.client.post("/post_us_phone", data={"phone": "123-456-789"})  # invalid format
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid US phone number", response.get_data(as_text=True))

    def test_us_ssn(self):
        """Form POST: ``US_SSN`` pattern validation."""
        # Positive test
        response = self.client.post("/post_us_ssn", data={"ssn": "123-45-6789"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '123-45-6789')

        # Negative tests
        response = self.client.post("/post_us_ssn", data={"ssn": "123-45-678"})  # too short
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid US Social Security Number", response.get_data(as_text=True))

        response = self.client.post("/post_us_ssn", data={"ssn": "123456789"})  # no dashes
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid US Social Security Number", response.get_data(as_text=True))

    def test_date(self):
        """Form POST: ``DATE`` pattern validation."""
        # Positive test
        response = self.client.post("/post_date", data={"date": "12/25/2023"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '12/25/2023')

        # Negative tests
        response = self.client.post("/post_date", data={"date": "13/45/2023"})  # invalid date
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date format", response.get_data(as_text=True))

    def test_guid(self):
        """Form POST: ``GUID`` pattern validation."""
        # Positive test
        response = self.client.post("/post_guid", data={"guid": "12345678-1234-1234-1234-123456789ABC"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '12345678-1234-1234-1234-123456789ABC')

        # Negative tests
        response = self.client.post("/post_guid", data={"guid": "invalid-guid"})  # invalid format
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid GUID format", response.get_data(as_text=True))

    def test_mac_address(self):
        """Form POST: ``MAC_ADDRESS`` pattern validation."""
        # Positive test
        response = self.client.post("/post_mac_address", data={"mac": "00:11:22:33:44:55"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '00:11:22:33:44:55')

        # Negative tests
        response = self.client.post("/post_mac_address", data={"mac": "00:11:22:33:44"})  # too short
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid MAC address format", response.get_data(as_text=True))

        response = self.client.post("/post_mac_address", data={"mac": "invalid-mac"})  # invalid format
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid MAC address format", response.get_data(as_text=True))

    def test_person_name(self):
        """Form POST: ``PERSON_NAME`` pattern validation."""
        # Positive test
        response = self.client.post("/post_person_name", data={"name": "John Doe"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'John Doe')

        # Negative tests
        response = self.client.post("/post_person_name", data={"name": "123"})  # numbers only
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid person name", response.get_data(as_text=True))

    def test_domain_name(self):
        """Form POST: ``DOMAIN_NAME`` pattern validation."""
        # Positive test
        response = self.client.post("/post_domain_name", data={"domain": "example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'example.com')

        # Negative tests
        response = self.client.post("/post_domain_name", data={"domain": "invalid..domain"})  # double dots
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid domain name", response.get_data(as_text=True))

    def test_text_basic(self):
        """Form POST: basic ``TEXT`` rule validation."""
        # Positive test
        response = self.client.post("/post_text_basic", data={"text": "Hello World"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'Hello World')

        # Negative tests
        response = self.client.post("/post_text_basic", data={"text": ""})  # empty
        self.assertEqual(response.status_code, 400)
        self.assertIn("longer than", response.get_data(as_text=True))

    def test_hex_color(self):
        """Form POST: ``HEX_COLOR`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_hex_color", data={"color": "#FF0000"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '#FF0000')

        response = self.client.post("/post_hex_color", data={"color": "#F00"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '#F00')

        response = self.client.post("/post_hex_color", data={"color": "#123ABC"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '#123ABC')

        # Negative tests
        response = self.client.post("/post_hex_color", data={"color": "#GGG"})  # invalid hex
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid hex color format", response.get_data(as_text=True))

        response = self.client.post("/post_hex_color", data={"color": "#12"})  # too short
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid hex color format", response.get_data(as_text=True))

    def test_slug(self):
        """Form POST: ``SLUG`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_slug", data={"slug": "hello-world"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'hello-world')

        response = self.client.post("/post_slug", data={"slug": "my-article-123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'my-article-123')

        # Negative tests
        response = self.client.post("/post_slug", data={"slug": "Hello World"})  # spaces and uppercase
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid slug format", response.get_data(as_text=True))

        response = self.client.post("/post_slug", data={"slug": "slug_with_underscores"})  # underscores
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid slug format", response.get_data(as_text=True))

    def test_base64(self):
        """Form POST: ``BASE64`` pattern validation."""
        # Positive test
        response = self.client.post("/post_base64", data={"data": "SGVsbG8gV29ybGQ="})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'SGVsbG8gV29ybGQ=')

        # Negative tests
        response = self.client.post("/post_base64", data={"data": "not-base64!"})  # invalid chars
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid base64 format", response.get_data(as_text=True))

    def test_semver(self):
        """Form POST: ``SEMVER`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_semver", data={"version": "1.2.3"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '1.2.3')

        response = self.client.post("/post_semver", data={"version": "2.0.0-beta.1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '2.0.0-beta.1')

        # Negative tests
        response = self.client.post("/post_semver", data={"version": "1.2"})  # missing patch
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid semantic version format", response.get_data(as_text=True))

        response = self.client.post("/post_semver", data={"version": "v1.2.3"})  # leading 'v'
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid semantic version format", response.get_data(as_text=True))

    def test_time_24h(self):
        """Form POST: ``TIME_24H`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_time_24h", data={"time": "14:30"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '14:30')

        response = self.client.post("/post_time_24h", data={"time": "09:15:30"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '09:15:30')

        # Negative tests
        response = self.client.post("/post_time_24h", data={"time": "25:00"})  # invalid hour
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid 24-hour time format", response.get_data(as_text=True))

        response = self.client.post("/post_time_24h", data={"time": "14:60"})  # invalid minute
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid 24-hour time format", response.get_data(as_text=True))

    def test_latitude(self):
        """Form POST: ``LATITUDE`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_latitude", data={"lat": "40.7128"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '40.7128')

        response = self.client.post("/post_latitude", data={"lat": "-33.8688"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '-33.8688')

        response = self.client.post("/post_latitude", data={"lat": "90.0"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '90.0')

        # Negative tests
        response = self.client.post("/post_latitude", data={"lat": "91.0"})  # out of range
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid latitude format", response.get_data(as_text=True))

        response = self.client.post("/post_latitude", data={"lat": "not-a-number"})  # invalid format
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid latitude format", response.get_data(as_text=True))

    def test_longitude(self):
        """Form POST: ``LONGITUDE`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_longitude", data={"lon": "-74.0060"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '-74.0060')

        response = self.client.post("/post_longitude", data={"lon": "151.2093"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '151.2093')

        response = self.client.post("/post_longitude", data={"lon": "180.0"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '180.0')

        # Negative tests
        response = self.client.post("/post_longitude", data={"lon": "181.0"})  # out of range
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid longitude format", response.get_data(as_text=True))

        response = self.client.post("/post_longitude", data={"lon": "not-a-number"})  # invalid format
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid longitude format", response.get_data(as_text=True))

    def test_currency(self):
        """Form POST: ``CURRENCY`` pattern validation."""
        # Positive tests
        response = self.client.post("/post_currency", data={"amount": "123.45"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '123.45')

        response = self.client.post("/post_currency", data={"amount": "100"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '100')

        response = self.client.post("/post_currency", data={"amount": "0.99"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), '0.99')

        # Negative tests
        response = self.client.post("/post_currency", data={"amount": "123.456"})  # too many decimal places
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid currency format", response.get_data(as_text=True))

        response = self.client.post("/post_currency", data={"amount": "abc"})  # non-numeric
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid currency format", response.get_data(as_text=True))

    def test_decorator_stacking(self):
        """Test that validation decorator works when stacked with other decorators."""
        # Positive test - should pass validation and show decorated attribute
        response = self.client.post("/test_decorator_stacking", data={"email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'Success: decorated')

        # Negative test - should fail validation
        response = self.client.post("/test_decorator_stacking", data={"email": "invalid-email"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email address", response.get_data(as_text=True))

    def test_exclude_validation_decorator(self):
        """Test the exclude_validation decorator."""
        # Health check should work without validation
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'OK')

        # API docs should work without validation
        response = self.client.get("/api/docs")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'API Documentation')

    def test_unprotected_route_detection(self):
        """Test detection of unprotected routes."""
        import flask_request_validate as fv

        # First make some requests to populate the registry
        self.client.post("/post_email", data={"email": "test@example.com"})
        self.client.get("/health")
        self.client.post("/unprotected", data={"data": "test"})

        # Check route security status
        status = fv.get_route_security_status()

        # Should have some protected routes
        self.assertGreater(status['protected_count'], 0)

        # Should have excluded routes
        self.assertGreater(status['excluded_count'], 0)

        # Check unprotected routes detection
        result = fv.check_unprotected_routes(self.app, warn_unprotected=False)

        # Should detect the unprotected POST route
        unprotected_endpoints = [route['endpoint'] for route in result['unprotected']]
        self.assertIn('POST /unprotected', unprotected_endpoints)

        # Excluded routes should be marked as such
        self.assertIn('GET /health', result['excluded'])
        self.assertIn('GET /api/docs', result['excluded'])


if __name__ == "__main__":
    unittest.main()

# response = self.client.post("/get_query_str_us_state_required", data={"content": "hello world"})
# https://flask.palletsprojects.com/en/3.0.x/testing/
