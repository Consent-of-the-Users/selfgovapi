from models import User
from routes.user import users_v1
from authorization import authorize_route
from before_request import request_attr
from flask import request


def has_valid_data(name, handle, email, uid):

    if not (name and handle and email and uid):
        return False

    handle_taken = User.load_by_attr("handle", handle)
    email_taken = User.load_by_attr("email", email)
    id_taken = User.load_by_uid(uid)
    
    if handle_taken or email_taken or id_taken:
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
        
        name, handle = request_attr("name"), request_attr("handle")
        email, uid = request_attr("email"), request_attr("uid")

        if not has_valid_data(name, handle, email, uid):
            return {"message": "Invalid data."}, 404

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

    user = User.load_by_uid(uid)
    if not user:
        return {"message": "Bad user uid."}, 404

    if request.method == "DELETE":
        user.delete()
        return {"message": "User deleted."}, 204
    
    if request.method == "PUT":
        name = request_attr(request, "name")
        handle = request_attr(request, "handle")
        email = request_attr(request, "email")
        
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

    # METHOD IS GET ===========================================================

    user_dict = user.to_dict()
    
    return {"message": "OK", "user": user_dict}, 200