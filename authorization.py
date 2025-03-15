from models import Client
from flask import request
from functools import wraps


unauthorized_message = {"message": "Unauthorized\n"}, 401

def error_message(msg, status_code=400):
    return {"message": msg}, status_code

def get_authorization_token(request):
    """
    Extracts the authorization token from the request headers, if present.
    """
    token = request.headers.get("Authorization")
    if not token or len(token) < 8:
        return None

    return token[7:]


def get_client_from_token(token):
    """
    Returns client based on given token if valid, else None.
    This otherwise redundant function wrapping around load_by_attr is needed for
    mocking in tests, in a way that is more descriptive within that domain.
    """
    return Client.load_by_attr("token", token)


def authorized_request(request):
    token = get_authorization_token(request)
    return get_client_from_token(token)
    

# wrapper to check for authorization token in request
def authorize_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not authorized_request(request):
            return unauthorized_message

        return func(*args, **kwargs)

    return wrapper
