import psycopg2
import os
from utils.updateTemplate import queueTemplate, roundTemplate

class Sql:
    def __init__(self):
        self.DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = None

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
        self.connect()
        cursor = self.conn.cursor()



        self.close()

    def getData(self, templateType):
        template = None
        self.connect()
        if templateType is 'Q':
            template = queueTemplate(True, 'January 2021', '792840405217050654', '813362652331114496', 3, 5, 1, '286838882392080384')

        self.close()
        return template
