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


def request_attr(attr):
    """
    Get the attribute from the request. For testing purposes.
    """
    from flask import request

    in_form = request.form.get(attr)

    return in_form if in_form else request.args.get(attr)


@app.before_request
def before_request():
    from flask import request

    token = get_authorization_token(request)

    set_request_token(token)

    client = Client.load_by_attr("token", token)

    set_request_client(client)
