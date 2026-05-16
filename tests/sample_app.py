"""
Flask **fixture application** (not a unittest module) used by ``test_validate.py``.

Defines one route per scenario (US state, numeric types, strings, cookies,
headers) so tests can drive the validator through real HTTP requests. See each
view’s docstring for which ``test_validate`` cases it supports.
"""

import os
import sys
from flask import Flask, render_template_string, request, Response
from functools import wraps
import json

# get the parent directory of directory containing this file
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

# pylint: disable=wrong-import-position
import flask_request_validate as fv
# pylint: disable=wrong-import-position

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
fv.HTML_WRAP_ERROR =  '{}</br>'

# HTML page for the test cases
FORM = '''
<html> 
<head>
    <script type="text/javascript" language="javascript">
        function state_optional() {
            if (document.getElementById("st").value == "") {
                document.getElementById("st").remove();
            }
            document.getElementById("state_optional").submit();
        }
    </script>
</head> 
<body> 
<h3>Required state</h3>
<form action="{{ url_for('get_us_state_required') }}" method="GET"> 
	<label for="Name">Enter a US state </label> 
	<input type="text" name="st"> 
	<button type="submit">Submit</button> 
</form> 
<h3>Optional state</h3>
<form action="{{ url_for('get_us_state_optional') }}" method="GET" ID="state_optional"> 
	<label for="Name">Enter a US state </label> 
	<input type="text" name="st" id="st"> 
	<button onclick="javascript:state_optional();">Submit</button> 
</form> 

</body> 
</html>
'''

# root directory
@app.route('/', methods=['GET'])
def get_root() -> Response:
    """Small HTML landing page with GET forms for manual state tests."""
    return render_template_string(FORM)


@app.route('/get_us_state_required', methods=['GET'])
@fv.validate({
            'query_string': {
                    'st': {'required': True, 'rules': fv.SAFE_US_STATE}
            }
        })
def get_us_state_required() -> Response:
    """``test_query_state``: required query param ``st`` (``SAFE_US_STATE``)."""
    return request.args['st']


@app.route('/get_us_state_optional', methods=['GET'])
@fv.validate({
            'query_string': {
                    'st': {'required': False, 'rules': fv.SAFE_US_STATE}
            }
        })
def get_us_state_optional() -> Response:
    """``test_query_state``: optional query param ``st`` (``SAFE_US_STATE``)."""
    if 'st' not in request.args:
        return 'missing state'

    return request.args['st']


@app.route('/post_us_state_required', methods=['POST'])
@fv.validate({
            'form': {
                    'st': {'required': True, 'rules': fv.SAFE_US_STATE}
            }
        })
def post_us_state_required() -> Response:
    """``test_form_state``: required form field ``st`` (``SAFE_US_STATE``)."""
    return request.form['st']


@app.route('/post_with_query_us_state_required', methods=['POST'])
@fv.validate({
            'query_string': {
                    'stq': {'required': True, 'rules': fv.SAFE_US_STATE}
            },
            'form': {
                    'stf': {'required': True, 'rules': fv.SAFE_US_STATE}
            }
        })
def post_with_query_us_state_required() -> Response:
    """``test_form_state``: required ``stq`` (query) + ``stf`` (form), both states."""
    return f'{request.args["stq"]}{request.form["stf"]}'


@app.route('/get_int', methods=['GET'])
@fv.validate({
            'query_string': {
                'test': {'required': True, 'rules':
                    {'min': 2, 'max': 10, 'type': 'int'}}
            }
        })
def get_int() -> Response:
    """``test_query_int``: query ``test`` as int, min 2 max 10."""
    return request.args['test']


@app.route('/post_int', methods=['POST'])
@fv.validate({
            'form': {
                'test': {'required': True, 'rules':
                    {'min': 2, 'max': 10, 'type': 'int'}}
            }
        })
def post_int() -> Response:
    """``test_form_int``: form ``test`` as int, min 2 max 10."""
    return request.form['test']


@app.route('/get_float', methods=['GET'])
@fv.validate({
            'query_string': {
                'test': {'required': True, 'rules':
                    {'min': 2.0, 'max': 35.5, 'type': 'float'}}
            }
        })
def get_float() -> Response:
    """``test_query_float``: query ``test`` as float, min 2.0 max 35.5."""
    return request.args['test']


@app.route('/post_float', methods=['POST'])
@fv.validate({
            'form': {
                'test': {'required': True, 'rules':
                    {'min': 2.0, 'max': 35.5, 'type': 'float'}}
            }
        })
def post_float() -> Response:
    """``test_form_float``: form ``test`` as float, min 2.0 max 35.5."""
    return request.form['test']


@app.route('/get_bool', methods=['GET'])
@fv.validate({
            'query_string': {
                'test': {'required': True, 'rules':
                    {'type': 'bool'}}
            }
        })
def get_bool() -> Response:
    """``test_query_bool``: query ``test`` as boolean string."""
    return request.args['test']


@app.route('/post_bool', methods=['POST'])
@fv.validate({
            'form': {
                'test': {'required': True, 'rules':
                    {'type': 'bool'}}
            }
        })
def post_bool() -> Response:
    """``test_form_bool``: form ``test`` as boolean string."""
    return request.form['test']


@app.route('/post_user', methods=['POST'])
@fv.validate({
            'form': {
                'username': {'required': True, 'rules': fv.SAFE_USERNAME}
            }
        })
def post_user() -> Response:
    """``test_username``: form ``username`` with default ``SAFE_USERNAME`` bounds."""
    return request.form['username']


@app.route('/post_different_user', methods=['POST'])
@fv.validate({
            'form': {
                'username': {'required': True, 'rules':
                             fv.set_min_max(fv.SAFE_USERNAME, 5, 8)}
            }
        })
def post_different_user() -> Response:
    """``test_username``: same field with ``set_min_max(SAFE_USERNAME, 5, 8)``."""
    return request.form['username']


@app.route('/post_text', methods=['POST'])
@fv.validate({
            'form': {
                'text': {'required': True, 'rules':
                         fv.set_min_max(fv.SAFE_TEXT, 4, -1)}
            }
        })
def post_text() -> Response:
    """``test_safetext``: form ``text`` with ``set_min_max(SAFE_TEXT, 4, -1)``."""
    return request.form['text']


@app.route('/get_cookie', methods=['GET'])
@fv.validate({
            'cookie': {
                'Acc-Sec': {'required': True, 'rules':
                         fv.set_min_max(fv.SAFE_TEXT, 4, -1)}
            }
        })
def get_cookie() -> Response:
    """``test_cookie``: cookie ``Acc-Sec`` with min-length safe text rules."""
    return request.cookies['Acc-Sec']


@app.route('/get_header', methods=['GET'])
@fv.validate({
            'header': {
                'Acc-Sec': {'required': True, 'rules':
                         fv.set_min_max(fv.SAFE_TEXT, 4, -1)}
            }
        })
def get_header() -> Response:
    """``test_header``: header ``Acc-Sec`` only (undeclared query args fail)."""
    return request.headers['Acc-Sec']


# Additional endpoints for comprehensive pattern testing

@app.route('/post_email', methods=['POST'])
@fv.validate({
            'form': {
                'email': {'required': True, 'rules': fv.EMAIL}
            }
        })
def post_email() -> Response:
    """Test EMAIL pattern validation."""
    return request.form['email']


# Custom error handler route for testing `on_error`
def custom_error_handler(validation_result):
    errors = validation_result.get('errors', [])
    payload = {'status': 'error', 'message': 'Validation failed', 'details': errors}
    return Response(json.dumps(payload), status=400, mimetype='application/json')


@app.route('/post_with_custom_error', methods=['POST'])
@fv.validate({
            'form': {
                'email': {'required': True, 'rules': fv.EMAIL}
            }
        }, on_error=custom_error_handler)
def post_with_custom_error() -> Response:
    """Endpoint used by tests to verify custom `on_error` handler."""
    return request.form['email']


@app.route('/post_url', methods=['POST'])
@fv.validate({
            'form': {
                'url': {'required': True, 'rules': fv.URL}
            }
        })
def post_url() -> Response:
    """Test URL pattern validation."""
    return request.form['url']


@app.route('/post_username_owasp', methods=['POST'])
@fv.validate({
            'form': {
                'username': {'required': True, 'rules': fv.USERNAME}
            }
        })
def post_username_owasp() -> Response:
    """Test USERNAME (OWASP) pattern validation."""
    return request.form['username']


@app.route('/post_password_strong', methods=['POST'])
@fv.validate({
            'form': {
                'password': {'required': True, 'rules': fv.PASSWORD_STRONG}
            }
        })
def post_password_strong() -> Response:
    """Test PASSWORD_STRONG pattern validation."""
    return request.form['password']


@app.route('/post_credit_card', methods=['POST'])
@fv.validate({
            'form': {
                'card': {'required': True, 'rules': fv.CREDIT_CARD}
            }
        })
def post_credit_card() -> Response:
    """Test CREDIT_CARD pattern validation."""
    return request.form['card']


@app.route('/post_us_zip', methods=['POST'])
@fv.validate({
            'form': {
                'zip': {'required': True, 'rules': fv.US_ZIP}
            }
        })
def post_us_zip() -> Response:
    """Test US_ZIP pattern validation."""
    return request.form['zip']


@app.route('/post_us_phone', methods=['POST'])
@fv.validate({
            'form': {
                'phone': {'required': True, 'rules': fv.US_PHONE}
            }
        })
def post_us_phone() -> Response:
    """Test US_PHONE pattern validation."""
    return request.form['phone']


@app.route('/post_us_ssn', methods=['POST'])
@fv.validate({
            'form': {
                'ssn': {'required': True, 'rules': fv.US_SSN}
            }
        })
def post_us_ssn() -> Response:
    """Test US_SSN pattern validation."""
    return request.form['ssn']


@app.route('/post_date', methods=['POST'])
@fv.validate({
            'form': {
                'date': {'required': True, 'rules': fv.DATE}
            }
        })
def post_date() -> Response:
    """Test DATE pattern validation."""
    return request.form['date']


@app.route('/post_guid', methods=['POST'])
@fv.validate({
            'form': {
                'guid': {'required': True, 'rules': fv.GUID}
            }
        })
def post_guid() -> Response:
    """Test GUID pattern validation."""
    return request.form['guid']


@app.route('/post_mac_address', methods=['POST'])
@fv.validate({
            'form': {
                'mac': {'required': True, 'rules': fv.MAC_ADDRESS}
            }
        })
def post_mac_address() -> Response:
    """Test MAC_ADDRESS pattern validation."""
    return request.form['mac']


@app.route('/post_person_name', methods=['POST'])
@fv.validate({
            'form': {
                'name': {'required': True, 'rules': fv.PERSON_NAME}
            }
        })
def post_person_name() -> Response:
    """Test PERSON_NAME pattern validation."""
    return request.form['name']


@app.route('/post_domain_name', methods=['POST'])
@fv.validate({
            'form': {
                'domain': {'required': True, 'rules': fv.DOMAIN_NAME}
            }
        })
def post_domain_name() -> Response:
    """Test DOMAIN_NAME pattern validation."""
    return request.form['domain']


@app.route('/post_text_basic', methods=['POST'])
@fv.validate({
            'form': {
                'text': {'required': True, 'rules': fv.TEXT}
            }
        })
def post_text_basic() -> Response:
    """Test basic TEXT rule validation."""
    return request.form['text']


# Additional endpoints for new pattern testing

@app.route('/post_hex_color', methods=['POST'])
@fv.validate({
            'form': {
                'color': {'required': True, 'rules': fv.HEX_COLOR}
            }
        })
def post_hex_color() -> Response:
    """Test HEX_COLOR pattern validation."""
    return request.form['color']


@app.route('/post_slug', methods=['POST'])
@fv.validate({
            'form': {
                'slug': {'required': True, 'rules': fv.SLUG}
            }
        })
def post_slug() -> Response:
    """Test SLUG pattern validation."""
    return request.form['slug']


@app.route('/post_base64', methods=['POST'])
@fv.validate({
            'form': {
                'data': {'required': True, 'rules': fv.BASE64}
            }
        })
def post_base64() -> Response:
    """Test BASE64 pattern validation."""
    return request.form['data']


@app.route('/post_semver', methods=['POST'])
@fv.validate({
            'form': {
                'version': {'required': True, 'rules': fv.SEMVER}
            }
        })
def post_semver() -> Response:
    """Test SEMVER pattern validation."""
    return request.form['version']


@app.route('/post_time_24h', methods=['POST'])
@fv.validate({
            'form': {
                'time': {'required': True, 'rules': fv.TIME_24H}
            }
        })
def post_time_24h() -> Response:
    """Test TIME_24H pattern validation."""
    return request.form['time']


@app.route('/post_latitude', methods=['POST'])
@fv.validate({
            'form': {
                'lat': {'required': True, 'rules': fv.LATITUDE}
            }
        })
def post_latitude() -> Response:
    """Test LATITUDE pattern validation."""
    return request.form['lat']


@app.route('/post_longitude', methods=['POST'])
@fv.validate({
            'form': {
                'lon': {'required': True, 'rules': fv.LONGITUDE}
            }
        })
def post_longitude() -> Response:
    """Test LONGITUDE pattern validation."""
    return request.form['lon']


@app.route('/post_currency', methods=['POST'])
@fv.validate({
            'form': {
                'amount': {'required': True, 'rules': fv.CURRENCY}
            }
        })
def post_currency() -> Response:
    """Test CURRENCY pattern validation."""
    return request.form['amount']


# Test decorator stacking compatibility
def example_decorator(func):
    """Example decorator that adds custom behavior."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Add some custom logic
        request.custom_attr = "decorated"
        return func(*args, **kwargs)
    return wrapper


@app.route('/test_decorator_stacking', methods=['POST'])
@example_decorator  # This decorator runs first
@fv.validate({      # This decorator runs second (validation happens here)
    'form': {
        'email': {'required': True, 'rules': fv.EMAIL}
    }
})
def test_decorator_stacking() -> Response:
    """Test that validation decorator works when stacked with other decorators."""
    return f"Success: {request.custom_attr}"


# Examples of excluded routes (no user input validation needed)
@app.route('/health', methods=['GET'])
@fv.exclude_validation("Health check endpoint")
def health_check() -> Response:
    """Health check endpoint that doesn't need validation."""
    return "OK"


@app.route('/api/docs', methods=['GET'])
@fv.exclude_validation("API documentation endpoint")
def api_docs() -> Response:
    """API documentation endpoint."""
    return "API Documentation"


# Example of an unprotected route (will be detected)
@app.route('/unprotected', methods=['POST'])
def unprotected_route() -> Response:
    """This route accepts POST data but has no validation - will be detected."""
    return f"Received: {request.form.get('data', 'nothing')}"


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()
