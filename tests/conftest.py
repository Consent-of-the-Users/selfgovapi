import pytest
from uuid import uuid4


# =============================================================================
# Basics, App and API =========================================================
# =============================================================================


@pytest.fixture()
def test_app():
    """
    Return the Flask app as configured for testing.
    """
    from main import app

    # configure the app for testing
    # SETUP
    app.config["TESTING"] = True

    # CLEAN UP
    yield app


@pytest.fixture()
def api(test_app):
    """
    Initiate the test_client() of the test app, renamed to 'api' so as to avoid
    confusion with client objects.
    """
    return test_app.test_client()


# =============================================================================
# Helper functions for fixtures ===============================================
# =============================================================================


def mock_with_patch(path):
    """
    Return a mock of the given path.
    """
    from unittest.mock import patch

    # A.1
    patcher = patch(path)
    mock = patcher.start()
    return mock

def normalized_put_method_name(method):
    """
    Normalize PUT method names into 'PUT'. This is required because PUT-VALID
    and PUT-INVALID are used in the method parameter to inform the
    is_valid_put_data fixture, allowing the parameterization of both types of requests. Then
    the actual method name must be normalized into a valid http method
    afterwards because it determines which request make_request will send.
    """
    if "PUT" in method or "put" in method:
        method = "PUT"
    if "POST" in method or "post" in method:
        method = "POST"
    return method


@pytest.fixture()
def make_request(api):
    """
    Return a function that makes requests of a given type to the test API. Optional authorization header.
    """

    def request_func(method, route, authorization=None, data={}):
        """
        Makes requests of a given type to the test API. Optional authorization header and PUT data.
        """
        if not isinstance(method, str):
            raise TypeError("Method must be a string")

        if method not in [
            "get",
            "post",
            "put",
            "delete",
            "GET",
            "POST",
            "PUT",
            "DELETE",
        ]:
            raise ValueError("Invalid HTTP method specified.")

        method = method.lower()

        if not isinstance(route, str):
            raise TypeError("Route must be a string")

        if not isinstance(data, (dict, type(None))):
            raise TypeError("Data must be a dictionary")

        headers = {}

        if authorization:
            headers["Authorization"] = f"Bearer {authorization}"

        method_func = getattr(api, method)
        return method_func(route, headers=headers, json=data)

    return request_func


# =============================================================================
# Parameterized fixtures ======================================================
# =============================================================================


@pytest.fixture(params=["GET", "POST-VALID", "POST-INVALID", "PUT-VALID", "PUT-INVALID", "DELETE"])
def method(request):
    """
    Parameterize the methods only, not routes. So GET /obj and GET /obj/{id}
    should be tested separately, not parameterized.
    """
    return request.param


@pytest.fixture(params=[True, False])
def is_authorized(request):
    """
    Parameterizes whether or not the request is authorized, mocks the necessary
    function if so, and returns an authorization token, else returns None.
    """
    # mocking the function used by the authorization wrapper
    mock_get_auth_client = mock_with_patch("authorization.get_client_from_token")
    if request.param:
        mock_get_auth_client.return_value = True
        return str(uuid4())
    else:
        mock_get_auth_client.return_value = None
        return None


@pytest.fixture()
def is_valid_put_data(request, method):
    """
    Parameterizes whether or not the data for PUT requests is valid. Informed
    by teh method parameter.
    """
    return {"data": "valid put data"} if method == "PUT-VALID" else {}

@pytest.fixture()
def is_valid_post_data(request, method):
    """
    Parameterizes whether or not the data for PUT requests is valid. Informed
    by teh method parameter.
    """
    return {"data": "valid post data"} if method == "POST-VALID" else {}


@pytest.fixture(params=[True, False])
def is_valid_id(request):
    """
    Paramererizes whether or not a given object id is valid in the request.
    Mocking the search for said objects must be done in-test, as this fixture
    can not receive an argument for which object is to be mocked from the test.
    """
    return str(uuid4()) if request.param else None


@pytest.fixture
def mock_resource(method, is_valid_id, is_valid_put_data):
    from unittest.mock import MagicMock
    # if is_valid_id, return function for mocking a given class & object (values can be overridden)
    # else, return function that mocks class but has it's load methods return None (values can be overridden)
    # this way, no matter if is_valid_id or not, I can call this function with resource being requested and
    # it will mock it correctly based on it's own knowledge of is_valid_id.
    def get_mock_resource(class_path, valid_id_return=False, valid_attr_return=False, invalid_id_return=False, invalid_attr_return=False, **to_dict_ret):
        '''
        class_path is used to patch in a class.
        An instance of that class will be mocked, given a uid = is_valid_id, and a .to_dict() method.
        The class will have mock .load_by_uid and .load_by_attr methods.
        -----------------------------------------------------------------------
        '''
        # MOCK INSTANCE =======================================================
        
        mock_obj = MagicMock()
        mock_obj.uid = is_valid_id

        # mock the .to_dict() method so it can be serialized
        to_dict = to_dict_ret if to_dict_ret else {"uid": is_valid_id}
        mock_obj.to_dict = MagicMock(return_value=to_dict)

        # MOCK CLASS ==========================================================

        mock_class = mock_with_patch(class_path)

        # if is_valid_id load methods return the instance/object, else None.
        # checking if valid/invalid_id_return allows you to override the specific return value if you want to.
        if is_valid_id:
            mock_class.load_by_uid.return_value = valid_id_return if valid_id_return is not False else mock_obj
        else:
            mock_class.load_by_uid.return_value = invalid_id_return if invalid_id_return is not False else None

        if is_valid_put_data and "PUT" in method:
            mock_class.load_by_attr.return_value = valid_attr_return if valid_attr_return is not False else None
        elif not is_valid_put_data and "PUT" in method:
            # put data is invalid if it's taken by another instance of that resource, which would
            # return an instance with a different uid
            mock_obj.uid = str(uuid4())
            mock_class.load_by_attr.return_value = invalid_attr_return if invalid_attr_return is not False else mock_obj

        return mock_class, mock_obj
    
    return get_mock_resource
