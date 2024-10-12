from routes.reaction import reactions_v1


@reactions_v1.route("/<chat_uid>", methods=["GET"], strict_slashes=False)
def reactions_by_chat(chat_uid):
    # return all reactions with that chat_uid
    return



@reactions_v1.route("/<chat_uid>/<from_uid>/<type>", methods=["GET", "POST", "DELETE"] strict_slashes=False)
def reactions_by_chat_user_type(chat_uid, from_uid, type):
    # if post, create reaction and save to firestore
    # if delete make sure you delete from firestore too
    return

