from routes.convo import convos_v1
from authorization import authorize_route, error_message
from flask import request
from models.convo import Convo
from models.user import User


def has_valid_data(user_uids):
    """
    Ensure user_uids are valid, there are exactly two of them, and that they do not already have a convo.
    :param user_uids: Comma-separated string of user UIDs.
    :return: List of User objects if valid, False otherwise.
    """
    import json
    from os import getenv

    if not user_uids:
        return False

    PRODUCTION = getenv("PRODUCTION")
    if not PRODUCTION:
        user_uids = json.loads(user_uids)
    else:
        user_uids = user_uids.split(",")

    if not type(user_uids) == list:
        return False

    if len(user_uids) != 2:
        return False

    participants = []

    for uid in user_uids:
        user_exists = User.load_by_uid(uid)
        if not user_exists:
            return False
        participants.append(user_exists)

    return participants


def create_convo(participants):
    """
    Create a new convo with the given participants.
    :param participants: List of User objects to add to the convo.
    :return: The created convo as a dictionary.
    """
    convo = Convo()
    convo.save()

    for participant in participants:
        convo.add_participant(participant)

    convo_dict = convo.to_dict()
    convo.save()

    return convo_dict


@convos_v1.route("/", methods=["POST"], strict_slashes=False)
@authorize_route
def all_convos():

    user_uids = request.form.get("users")

    participants = has_valid_data(user_uids)
    if not participants:
        return error_message("Invalid data.")

    try:
        convo_dict = create_convo(participants=participants)
    except Exception as e:
        return error_message(f"Error creating convo: {str(e)}")
    return {"message": "Convo created.", "convo": convo_dict}, 201


@convos_v1.route(
    "/<participant_one>/<participant_two>",
    methods=["GET", "POST"],
    strict_slashes=False,
)
@authorize_route
def get_convo_by_participants(participant_one, participant_two):

    user_uids = [participant_one, participant_two]

    valid_data = has_valid_data(user_uids)
    if not valid_data:
        return error_message("Invalid participants.", 404)

    convo = Convo.load_by_participants(valid_data)

    if request.method == "POST":
        if convo:
            return {"message": "Convo already exists."}, 409

        participant_one = User.load_by_uid(participant_one)
        participant_two = User.load_by_uid(participant_two)

        participants = [participant_one, participant_two]
        try:
            convo_dict = create_convo(participants=participants)
        except Exception as e:
            return error_message(f"Error creating convo: {str(e)}")
        uid = convo_dict.get("uid")
        return {"message": "Convo created.", "uid": uid}, 201

    # convo.participants # loading into memory
    if not convo:
        return error_message("Invalid data.", 404)

    convo_uid = get_convo_uid(convo)

    return {"message": "OK", "uid": convo_uid}, 200


def get_convo_uid(convo):
    """
    Helper function to make mocking easier in tests.
    """
    return convo.uid if convo else None


"""

Create groop flow:
POST /groops
-name -handle -description -member uids
* creates a MasterGroopConvo
save to firestore
return groop

frontend:
query all groops on groop page
query all convos on conversations page includes MasterGroopConvo
change check for convo.is_groop to convo.type == groop_convo or master_groop_convo

normalize the way request.args and request.form are used to work both locally and in production
"""


# ============


def are_valid_participants(user_ids):
    from models.user import User

    for user_id in user_ids:
        if not User.load_by_uid(user_id):
            return False
    return True


"""
@convos_v1.route("/", methods=["GET"], strict_slashes=False)
@authorize_route
def convo_by_user_ids():
    from models import User

    user_ids = request.args.get('users', '').split(',')
    is_group = request.args.get('is_group', False)
    title = request.args.get('title', '')

    if request.method == 'POST':
        # obsolete new conversation button on convo page in top right of appbar
        import json
        user_ids = request.form.get("users")
        user_ids_cleaned = json.loads(user_ids)
        is_group = request.form.get("is_group")
        title = request.form.get("title")

    if request.method == "GET":
        # 
        # Join the list into a single string and then proceed to clean it
        user_ids_cleaned = ','.join(user_ids).strip('[]').split(',')

        # Remove the quotes from each user ID
        user_ids_cleaned = [user_id.strip(' "') for user_id in user_ids_cleaned]

    user_ids = user_ids_cleaned
    myset = set(user_ids)
    user_ids = list(myset)

    if is_group == "true" or is_group == "True":
        is_group = True
    elif is_group == "false" or is_group == "False":
        is_group = False
    else:
        is_group = False

    if not user_ids:
        user_ids = [uid for uid in request.args.get("users")]

    if not user_ids:
        # retrieve them another way
        user_ids = request.args.getlist('users')

    if not user_ids:
        return {"message": "No user ids provided."}, 400
    
    if len(user_ids) < 2:
        return {"message": "At least two user ids are required."}, 400
    
    if not are_valid_participants(user_ids):
        return {"message": "Invalid user ids."}, 404
    
    if request.method == 'POST':
        # Create a new convo with the provided user IDs

        try:
            data = {
                'is_group': is_group,
                'title': title
            }
            convo = convo(**data)
        except Exception as e:
            return {"message": f"Error creating convo: {str(e)}"}, 500

        for uid in user_ids:
            user = User.load_by_uid(uid)
            if not user:
                raise ValueError(f"User with ID {uid} not found")
            if user not in convo.participants:
                convo.participants.append(user)
        convo.save()
        return {"message": "convo created.", "uid": convo.uid}, 201

    
    convo = convo.load_by_user_ids_and_is_group(user_ids, is_group)
    if not convo:
        return {"message": "No convo found."}, 404
    

    return {"message": "OK", "uid": convo.uid}, 200



@convos_v1.route("<convo_id>/participants/<user_id>", methods=["DELETE"], strict_slashes=False)
@authorize_route
def remove_participant(convo_id, user_id):
    from models.convo import convo
    from models.user import User

    convo = convo.load_by_uid(convo_id)
    if not convo:
        return {"message": "No convo found."}, 404

    user = User.load_by_uid(user_id)
    if not user:
        return {"message": "User not found."}, 404

    if user in convo.participants:
        convo.participants.remove(user)
        convo.save()
        if len(convo.participants) == 0:
            convo.delete()
        return {"message": "Participant removed."}, 200
    else:
        return {"message": "Participant not found in the convo."}, 404"

        


"""
