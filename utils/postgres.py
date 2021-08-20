import psycopg2
import os


def connect_to_postgres():
    return psycopg2.connect(os.getenv('POSTGRES_URL'), sslmode='require')


def get_character_dicts():
    conn = connect_to_postgres()
    cur = conn.cursor()

    cur.execute("select * from unit_name")
    character_dict = cur.fetchall()

    cur.execute("select * from alt_version_name")
    alt_dict = cur.fetchall()

    return character_dict, alt_dict


def update_tl_tables():
    pass
