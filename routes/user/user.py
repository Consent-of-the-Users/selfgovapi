from models import User
from routes.user import users_v1
from authorization import authorize_route
from before_request import get_attr_from_request_form
from flask import request


def has_valid_data(request):
    user_name = request.form.get("name")
    user_handle = request.form.get("handle")
    user_email = request.form.get("email")

    # name_taken = User.load_by_attr("name", user_name)
    handle_taken = User.load_by_attr("handle", user_handle)
    email_taken = User.load_by_attr("email", user_email)

    if not user_name:
        return False
    if not user_handle or handle_taken:
        return False
    if not user_email or email_taken:
        return False
    return True


def create_user(**data):
    user = User(**data)
    user_dict = user.to_dict()
    user.save()
    return user_dict

@users_v1.route("/", methods=["GET", "POST"], strict_slashes=False)
@authorize_route
def all_users():

    if request.method == "POST":
        if not has_valid_data(request):
            return {"message": "Invalid data."}, 404

        name = request.form.get("name")
        handle = request.form.get("handle")
        email = request.form.get("email")
        data = {
            "name": name,
            "handle": handle,
            "email": email,
        }
        user_dict = create_user(**data)
        return {"message": "User created successfully.", "user": user_dict}, 201

    users = User.load_all_dict(remove_attr="client_id")
    return {"users": users}, 200


@users_v1.route("/<id>", methods=["GET", "DELETE", "PUT"], strict_slashes=False)
@authorize_route
def users_by_id(id):

    user = User.load_by_id(id)
    if not user:
        return {"message": "Bad user id."}, 404

    user_dict = user.to_dict()

    if request.method == "DELETE":
        user.delete()
        return {"message": "User deleted."}, 204
    
    if request.method == "PUT":
        name = get_attr_from_request_form(request, "name")
        
        if User.load_by_attr("name", name):
            return {"message": "user name taken."}, 400

        user.name = name
        user.save()
        
        return {"message": "user updated."}, 204

    
    return {"message": "OK", "user": user_dict}, 200