from routes.conversation import conversations_v1
from authorization import authorize_route
from flask import request
from models.conversation import Conversations

def are_valid_participants(user_ids):
    from models.user import User

    for user_id in user_ids:
        if not User.load_by_id(user_id):
            return False
    return True

@conversations_v1.route("/", methods=["GET", "POST"], strict_slashes=False)
@authorize_route
def conversation_by_user_ids():
    from models import User

    user_ids = request.args.get('users', '').split(',')
    is_group = request.args.get('is_group', False)

    if request.method == 'POST':
        import json
        user_ids = request.form.get("users")
        user_ids_cleaned = json.loads(user_ids)
        is_group = request.form.get("is_group")

    if request.method == "GET":
        # Join the list into a single string and then proceed to clean it
        user_ids_cleaned = ','.join(user_ids).strip('[]').split(',')

        print("INITIAL USER IDS", user_ids_cleaned)
        # Remove the quotes from each user ID
        user_ids_cleaned = [user_id.strip(' "') for user_id in user_ids_cleaned]

    user_ids = user_ids_cleaned
    myset = set(user_ids)
    user_ids = list(myset)

    if is_group:
        is_group = True
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
        # Create a new conversation with the provided user IDs

        try:
            data = {
                'is_group': is_group
            }
            conversation = Conversations(**data)
        except Exception as e:
            return {"message": f"Error creating conversation: {str(e)}"}, 500

        for uid in user_ids:
            user = User.load_by_id(uid)
            if not user:
                raise ValueError(f"User with ID {uid} not found")
            if user not in conversation.participants:
                conversation.participants.append(user)
        conversation.save()
        return {"message": "Conversation created.", "uid": conversation.uid}, 201

    
    conversation = Conversations.load_by_user_ids_and_is_group(user_ids, is_group)
    if not conversation:
        return {"message": "No conversation found."}, 404
    

    return {"message": "OK", "uid": conversation.uid}, 200


@conversations_v1.route("<convo_id>/participants/<user_id>", methods=["DELETE"], strict_slashes=False)
@authorize_route
def remove_participant(convo_id, user_id):
    from models.conversation import Conversations
    from models.user import User

    conversation = Conversations.load_by_id(convo_id)
    if not conversation:
        return {"message": "No conversation found."}, 404

    user = User.load_by_id(user_id)
    if not user:
        return {"message": "User not found."}, 404

    if user in conversation.participants:
        conversation.participants.remove(user)
        conversation.save()
        return {"message": "Participant removed."}, 200
    else:
        return {"message": "Participant not found in the conversation."}, 404