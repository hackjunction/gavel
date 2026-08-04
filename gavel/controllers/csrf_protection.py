from gavel import app
import gavel.utils as utils
from flask import abort, request, session

@app.before_request
def csrf_protect():
    if request.method == "POST" and not request.path.startswith("/api/"):
        token = session.get('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

@app.before_request
def api_protect():
    if request.method == "POST" and request.path.startswith("/api/"):
        authorization = request.headers.get("x-access-token")
        if not authorization:
            abort(401)
        username, password = authorization.split(':')
        if not utils.check_auth(username, password):
            abort(401)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = utils.gen_secret(32)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token
