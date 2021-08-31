import discord.ext.commands.errors
import psycopg2
import os


def connect_to_postgres():
    return psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')


def get_character_dicts():
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        try:
            cur.execute("select * from unit_name")
            character_dict = cur.fetchall()

            cur.execute("select * from alt_version_name")
            alt_dict = cur.fetchall()
            return character_dict, alt_dict
        except (discord.ext.commands.errors.CommandInvokeError, AttributeError) as e:
            print(e)
        finally:
            conn.close()


def update_tl_tables():
    pass


def get_roles():
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        try:
            cur.execute("select * from roles")
            return cur.fetchall()
        except (discord.ext.commands.errors.CommandInvokeError, AttributeError) as e:
            print(e)
        finally:
            conn.close()


def add_role(role_id, role_name):
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        try:
            cur.execute(
                "insert into roles values (%s, %s) on conflict (role_id) do update set role_name=%s;", (role_id, role_name, role_name)
            )
            conn.commit()
        except (discord.ext.commands.errors.CommandInvokeError, AttributeError) as e:
            print(e)
        finally:
            conn.close()


def remove_role(role_id):
    conn = connect_to_postgres()
    with conn.cursor() as cur:
        try:
            cur.execute(
                f"delete from roles where role_id=%s", role_id
            )
        except (discord.ext.commands.errors.CommandInvokeError, AttributeError) as e:
            print(e)
        finally:
            conn.close()

