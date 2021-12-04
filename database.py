import os
from flask_sqlalchemy import SQLAlchemy
class DB:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    def __init__(self,app):
        self.app = app
        self.__Initialize()
    def __Initialize(self):
        if self.app:
            try:
                self.app.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
                self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = self. SQLALCHEMY_TRACK_MODIFICATIONS
                self.db = SQLAlchemy(self.app)
                print("[INFO] Initialized Flask SQL Alchemy")
            except Exception as e:
                print("[ERROR] Failed to initialize Flask SQL Alchemy")
                print(e)
        else:
            print("[ERROR] 'App' is not defined")
    def CreateDB(self):
        if not os.path.exists('./database/test.db'):
            try:
                self.db.create_all()
                print("[INFO] Database Created Succesfully")
            except Exception as e:
                print("[ERROR] Error in creating database")
                print(e)
    def GetDB(self):
        if self.db:
            return self.db
        else:
            print("[ERROR] 'db' is not defined")
            return None