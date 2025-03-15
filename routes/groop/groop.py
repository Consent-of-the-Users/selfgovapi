from routes.groop import groops_v1
from authorization import authorize_route, error_message
from before_request import request_attr
from flask import request
from models.groop import Groop
from models.convo import Convo
from models.groop_convo import GroopConvo
from models.master_groop_convo import MasterGroopConvo


def has_valid_data(name, handle, description):
    
    if not (name and handle and description):
        return False
    
    if Groop.load_by_attr("handle", handle):
        return False
    
    return True


def create_groop(**data):
    groop = Groop(**data)
    master_convo = groop.master_convo()
    groop_dict = groop.to_dict()
    groop.save()
    return groop_dict


@groops_v1.route('/', methods=['POST'], strict_slashes=False)
def all_groops():

    name, members = request_attr("name"), request_attr("members")
    description, handle = request_attr("description"), request_attr("handle")

    if request.method == "POST":

        if not has_valid_data(name, handle, description):
            return error_message("Invalid data.", 404)
        
        data = {
            "name": name,
            "handle": handle,
            "description": description,
            "members": members
        }
        try:
            groop_dict = create_groop(**data)
        except Exception as e:
            print(e)
            return error_message(str(e), 500)
        return {"message": "Groop created successfully.", "groop": groop_dict}, 201
