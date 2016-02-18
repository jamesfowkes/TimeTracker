"""
client_controller.py
"""

from datetime import datetime

from TimeTracker.db import db

class Client(db.Model):

    __tablename__ = "Clients"

    ClientID = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    Address = db.Column(db.String)
    Email = db.Column(db.String)

    def __repr__(self):
        return "<Client(ClientID='%s', Name='%s', Address='%s', Email='%s')>" % (
            self.ClientID, self.Name, self.Address, self.Email)

    @classmethod
    def get_all(cls):
        query = cls.query
        return query.all()

    @classmethod
    def get(cls, ClientID):
        query = cls.query
        query = query.filter(Client.ClientID == ClientID)
        return query.one()

    def insert(self):
        db.session().commit()