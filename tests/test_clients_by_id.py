from authorization import unauthorized_message
from conftest import normalized_put_method_name, mock_with_patch
import pytest
from uuid import uuid4
from unittest.mock import MagicMock


def test_client_by_id(method, is_valid_id, is_authorized, is_valid_put_data, make_request, mock_resource):
    """
    Test the /clients/uid endpoint with the following parameters:
    - HTTP methods
    - Authorization header
    - Valid and invalid put data
    """

    # SETUP & MOCK ============================================================
    method = normalized_put_method_name(method)
    
    mock_class, mock_obj = mock_resource("routes.client.client.Client")

    client_id = is_valid_id if is_valid_id else str(uuid4())

    # mock updating data during PUT requests
    get_attr_from_request_form = mock_with_patch("routes.client.client.get_attr_from_request_form")
    get_attr_from_request_form.return_value = False
    if method == "PUT" and is_valid_id and is_authorized and is_valid_put_data:
        get_attr_from_request_form.return_value = True 

    # ACTION ==================================================================
    response = make_request(
        method,
        f"/v1/clients/{client_id}/",
        authorization=is_authorized,
        data=is_valid_put_data,
    )

    # ASSERTIONS ==============================================================
    # The order of these conditions is important and aligns with Flask's behavior.

    if not method in ["GET", "PUT"]:
        # method not allowed
        assert response.status_code == 405
        return

    if not is_authorized:
        # method allowed but request not authorized
        assert response.status_code == 401
        # assert response.get_json() == unauthorized_message[0]
        return
    
    if not is_valid_id:
        # method allowed and request authorized but nothing found due to bad uid
        assert response.status_code == 404
        return
    
    # TODO: In the future, ensure only the client being requested can perform the request.
    # is_valid_id == client.uid found via authorization token. This may involve adding another
    # parameter to mock_resource. If token-found client.uid is/isn't = is_valid_id.

    if method == "PUT":
        if not is_valid_put_data:
            # method allowed, request authorized, valid id, but put data is invalid
            assert response.status_code == 400
            return
        else:
            # method allowed, request authorized, valid id, put data valid, updated
            assert response.status_code == 204
            return
    elif method == "DELETE":
        # DISABLING DELETE FOR THE TIME BEING AS POTENTIAL SECURITY ISSUE
        # method allowed, request authorized, valid id, deleted
        assert response.status_code == 204
        return

    # method allowed, request authorized, valid id, GET request
    assert response.status_code == 200
    assert mock_obj.uid == is_valid_id
    assert response.get_json().get("client") == mock_obj.to_dict()
