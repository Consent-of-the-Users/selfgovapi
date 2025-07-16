import pytest
from authorization import unauthorized_message
from conftest import normalized_put_method_name, mock_with_patch
from uuid import uuid4


def test_get_convo_by_participants(
    method, is_authorized, is_valid_id, make_request, mock_resource
):
    """
    Test the /convos/<participant_one>/<participant_two> endpoint with the following parameters:
    - HTTP methods
    - Authorization header
    - Valid and invalid put data
    """

    # SETUP & MOCK ============================================================
    method = normalized_put_method_name(method)

    user_one = is_valid_id if is_valid_id else str(uuid4())
    user_two = is_valid_id if is_valid_id else str(uuid4())

    mock_convo_class, mock_convo = mock_resource("routes.convo.convo.Convo")

    if is_valid_id and method == "POST":
        mock_convo_class.load_by_participants.return_value = None
    elif is_valid_id and method == "GET":
        mock_get_convo_uid = mock_with_patch("routes.convo.convo.get_convo_uid")
        mock_get_convo_uid.return_value = mock_convo.uid

    print(
        "mock convo class",
        mock_convo_class,
        "mock convo",
        mock_convo,
        "mock convo return",
        mock_convo_class.load_by_participants.return_value,
    )

    mock_has_valid_data = mock_with_patch("routes.convo.convo.has_valid_data")
    mock_has_valid_data.return_value = mock_convo if is_valid_id else None

    print("has valid data mock", mock_has_valid_data)

    # ACTION ==================================================================

    response = make_request(
        method,
        "/v1/convos/{}/{}".format(user_one, user_two),
        authorization=is_authorized,
    )

    # ASSERTIONS ==============================================================

    if method not in ["GET", "POST"]:
        assert response.status_code == 405
        return

    if not is_authorized:
        assert response.status_code == 401
        assert response.get_json() == unauthorized_message[0]
        return

    if not is_valid_id:
        assert response.status_code == 404
        return

    if method == "POST":
        if is_valid_id:
            assert response.status_code == 201
            return
        else:
            assert response.status_code == 404
            return

    assert response.status_code == 200
    assert "token" not in response.get_json()
