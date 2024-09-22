from main import app
from models import Client
from authorization import get_authorization_token


def set_request_token(token):
    from flask import request

    request.token = token
    if not token:
        request.client = None

    return


def set_request_client(client):
    from flask import request

    request.client = client
    if not client:
        request.token = None

    return


def get_attr_from_request_form(request, attr):
    """
    Get the attribute from the request. For testing purposes.
    """
    in_form = request.form.get(attr)
    if in_form:
        return in_form
    in_arg = request.args.get(attr)
    return in_arg


@app.before_request
def before_request():
    from flask import request

    token = get_authorization_token(request)

    set_request_token(token)

    if not token:
        return

    client = Client.load_by_attr("token", token)

    set_request_client(client)
