def get_args(args):
    role_id = None
    admin = False
    for arg in args:
        if arg[3:-1].isnumeric():
            role_id = arg[3:-1]
        if 'a' == arg:
            admin = True

    return role_id, admin
