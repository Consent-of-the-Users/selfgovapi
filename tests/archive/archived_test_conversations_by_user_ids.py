from authorization import unauthorized_message
from conftest import normalized_put_method_name
import pytest


# THIS file has been archived because local and production requests are so
# different due to flutterflow quirks. I can't seem to mimick the way the
# actual FlutterFlow requests send dynamic numbers of query parameters.
# I wrote the tests prior to writing local code, and it worked great, but
# then I had to change the production code so much to accommodate FF that
# correcting the tests would just be writing tests TO the code rather than TDD,
# even if I could mimic the requests correctly.

def test_get_conversation_by_user_list(method, make_request, is_authorized, is_valid_post_data):
    """
    Test the GET /conversations/ endpoint.
    Should receive a list of user.uids and return a conversation with those and only those participants.
    """
    method = normalized_put_method_name(method)

    from conftest import mock_with_patch
    mock_class = mock_with_patch("routes.conversation.conversation.are_valid_participants")
    mock_class.return_value = True

    if method == "POST" and not is_valid_post_data:
        mock_class.return_value = False
        

    response = make_request(method, "/v1/conversations/?users=1,12,123", authorization=is_authorized)

    if not method in ["GET", "POST"]:
        assert response.status_code == 405
        return
    
    if not is_authorized:
        assert response.status_code == 401
        assert response.get_json() == unauthorized_message[0]
        return
    
    if method == "POST":
        if not is_valid_post_data:
            assert response.status_code == 404
            return
        else:
            assert response.status_code == 201
            return
    
    assert response.status_code == 200