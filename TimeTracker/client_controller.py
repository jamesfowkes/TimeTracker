"""
client_controller.py
"""

from datetime import datetime

from TimeTracker.db import session
from TimeTracker.base import Base

from sqlalchemy import Column, Integer, String, func

class Client(Base):

    __tablename__ = "Clients"

    ClientID = Column(String, primary_key=True)
    Name = Column(String)
    Address = Column(String)
    Email = Column(String)

    def __repr__(self):
        return "<Client(ClientID='%s', Name='%s', Address='%s', Email='%s')>" % (
            self.ClientID, self.Name, self.Address, self.Email)

    @classmethod
    def get_all(cls):
        query = session().query(Client)
        return query.all()

    @classmethod
    def get(cls, ClientID):
        query = session().query(Client)
        query = query.filter(Client.ClientID == ClientID)
        return query.one()

    def insert(self):
        session().add(self)
        session().commit()