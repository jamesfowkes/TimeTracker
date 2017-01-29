"""
client_controller.py
"""

import logging

from datetime import datetime

from TimeTracker.controllers.address_controller import Address

from TimeTracker.db import db

def get_module_logger():
    return logging.getLogger(__name__)

class Client(db.Model):

    __tablename__ = "Clients"

    ClientID = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    Email = db.Column(db.String)

    def __repr__(self):
        return "<Client(ClientID='%s', Name='%s', Email='%s')>" % (
            self.ClientID, self.Name, self.Email)

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
        db.session().add(self)
        db.session().commit()

    @property
    def Address(self):
        addresses = Address.get_for_client(self.ClientID)
        return addresses[-1].Address
