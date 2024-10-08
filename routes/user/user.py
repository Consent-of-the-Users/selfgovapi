from models import User
from routes.user import users_v1
from authorization import authorize_route
from before_request import get_attr_from_request_form
from flask import request


def has_valid_data(request):
    user_name = request.form.get("name")
    user_handle = request.form.get("handle")
    user_email = request.form.get("email")
    user_id = request.form.get("uid")

    # name_taken = User.load_by_attr("name", user_name)
    handle_taken = User.load_by_attr("handle", user_handle)
    email_taken = User.load_by_attr("email", user_email)
    id_taken = User.load_by_id(user_id)

    if not user_id or id_taken:
        return False
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
    user.save(firestore=False)
    return user_dict

@users_v1.route("/", methods=["GET", "POST"], strict_slashes=False)
@authorize_route
def all_users():

    if request.method == "POST":
        if not has_valid_data(request):
            return {"message": "Invalid data."}, 404

        name = get_attr_from_request_form(request, "name")
        handle = get_attr_from_request_form(request, "handle")
        email = get_attr_from_request_form(request, "email")
        uid = get_attr_from_request_form(request, "uid")

        data = {
            "name": name,
            "handle": handle,
            "email": email,
            "uid": uid
        }
        try:
            user_dict = create_user(**data)
        except Exception as e:
            print(e)
            return {"message": str(e)}, 500
        return {"message": "User created successfully.", "user": user_dict}, 201

    users = User.load_all_dict(remove_attr="client_id")
    return {"users": users}, 200


@users_v1.route("/<uid>", methods=["GET", "DELETE", "PUT"], strict_slashes=False)
@authorize_route
def users_by_id(uid):

    user = User.load_by_id(uid)
    if not user:
        return {"message": "Bad user uid."}, 404

    user_dict = user.to_dict()

    if request.method == "DELETE":
        user.delete()
        return {"message": "User deleted."}, 204
    
    if request.method == "PUT":
        name = get_attr_from_request_form(request, "name")
        handle = get_attr_from_request_form(request, "handle")
        email = get_attr_from_request_form(request, "email")
        
        handle_taken = User.load_by_attr("handle", handle)
        if handle_taken and not handle_taken.uid == uid:
            return {"message": "user handle taken."}, 400
        
        email_taken = User.load_by_attr("email", email)
        if email_taken and not email_taken.uid == uid:
            return {"message": "user email taken."}, 400

        if name:
            user.name = name
        if handle:
            user.handle = handle
        if email:
            user.email = email
        user.save()
        
        return {"message": "user updated."}, 204

    
    return {"message": "OK", "user": user_dict}, 200