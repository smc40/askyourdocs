import contextvars

user_id = contextvars.ContextVar('user_id', default=None)

def get_current_user_id():
    return user_id.get()
