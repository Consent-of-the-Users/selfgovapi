import pytest
from authorization import unauthorized_message
from conftest import normalized_put_method_name, mock_with_patch


def test_all_convos(method, is_authorized, is_valid_post_data, make_request):
    """
    Test the /convos endpoint with the following parameters:
    - HTTP methods
    - Authorization header
    - Valid and invalid put data
    """

    # SETUP & MOCK ============================================================
    method = normalized_put_method_name(method)

    mock_create_convo = mock_with_patch("routes.convo.convo.create_convo")
    mock_has_valid_data = mock_with_patch("routes.convo.convo.has_valid_data")

    # if it's a valid POST request, the request should have valid data and convo should be created, else no.
    mock_has_valid_data.return_value = is_valid_post_data
    mock_create_convo.return_value = is_valid_post_data

    # ACTION ==================================================================

    response = make_request(
        method, "/v1/convos/", data=is_valid_post_data, authorization=is_authorized
    )

    # ASSERTIONS ==============================================================

    if method not in ["POST"]:
        assert response.status_code == 405
        return

    if not is_authorized:
        assert response.status_code == 401
        assert response.get_json() == unauthorized_message[0]
        return
    
    if method == "POST":
        if not is_valid_post_data:
            assert response.status_code == 400
            return
        else:
            assert response.status_code == 201
            return

    assert response.status_code == 200
    assert "convos" in response.get_json()
    assert isinstance(response.get_json().get("convos"), list)
    assert "token" not in response.get_json()