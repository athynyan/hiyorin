import psycopg2
import os
from utils.updateTemplate import queueTemplate

class Sql:
    def __init__(self):
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
        except:
            print('Error connection.')

    def close(self):
        try:
            self.conn.close()
        except:
            print('No ongoing connection.')

    def update(self, template):
        cursor = conn.cursor()

    def getData(self):
        return
