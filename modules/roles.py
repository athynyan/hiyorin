from utils import postgres


def add_role(role_id, guild_roles, admin_role):
    for role in guild_roles:
        print(role.id)
        print(role_id)
        if role_id == role.id:
            postgres.add_role(role.id, role.name, admin_role)


def remove_role(role_id, guild_roles):
    for role in guild_roles:
        if role_id == role.id:
            postgres.remove_role(role_id)