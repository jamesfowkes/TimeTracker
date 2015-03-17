"""
client_controller.py
"""

from datetime import datetime

from TimeTracker.db import select

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
        return "<Client(ClientID='%s', Name='%s', Address='%d', Email='%d')>" % (
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

    @staticmethod
    def get_months_when_worked_for_client(ClientID):

        start_of_current_month = datetime(datetime.now().year, datetime.now().month, 1)

        data = select(["Start"], "Tasks", "ClientID='%s'" % ClientID)
        unique_months = set()
        for row in data:
            this_row_date = datetime.fromtimestamp(row['Start'])
            if this_row_date < start_of_current_month: # Only include complete months
                start_of_month_date = datetime(this_row_date.year, this_row_date.month, 1)
                unique_months.add(start_of_month_date)

        return unique_months