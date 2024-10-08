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

    if request.method == 'POST':
        import json
        user_ids = request.form.get("users")
        user_ids_cleaned = json.loads(user_ids)

    if request.method == "GET":
        # Join the list into a single string and then proceed to clean it
        user_ids_cleaned = ','.join(user_ids).strip('[]').split(',')

        print("INITIAL USER IDS", user_ids_cleaned)
        # Remove the quotes from each user ID
        user_ids_cleaned = [user_id.strip(' "') for user_id in user_ids_cleaned]

    user_ids = user_ids_cleaned
    myset = set(user_ids)
    user_ids = list(myset)

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
            conversation = Conversations()
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

    
    conversation = Conversations.load_by_user_ids(user_ids)
    if not conversation:
        return {"message": "No conversation found."}, 404
    

    return {"message": "OK", "uid": conversation.uid}, 200
