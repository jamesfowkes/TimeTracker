"""
oneoff_controller.py
"""

import logging

from time import mktime
from datetime import datetime, timezone
from calendar import monthrange

from TimeTracker.controllers.invoice_controller import Invoice
from TimeTracker.display_helper import get_sort_key

from TimeTracker.db import session
from TimeTracker.base import Base

from TimeTracker.utility import month_number

from sqlalchemy import Column, Integer, String, ForeignKey

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

class OneOff(Invoice, Base):

    __tablename__ = "OneOffs"

    Name = Column(String)
    ClientID = Column(String, ForeignKey("Clients.ClientID"), primary_key=True)
    Charge = Column(Integer)
    Hours = Column(Integer)
    Date = Column(Integer, primary_key=True)
    State = Column(Integer)
    NumericID = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<OneOff(name='%s', ClientID='%s', charge='%d', hours='%d', date='%d', State='%d', NumericID='%d')>" % (
            self.Name, self.ClientID, self.Charge, self.Hours, self.Date, self.State, self.NumericID)

    def set_state(self, State):
        self.State = self.get_possible_states().index(State)

        get_module_logger().info("New State = %d", self.State)

        session().commit()

    def get_state(self):
        return self.State

    def num(self):
        return self.NumericID

    def date(self):
        return datetime.fromtimestamp(self.Date)

    def reference(self):
        return "%s-%s-%d" % (self.ClientID, self.format_date(), self.NumericID)

    def format_date(self, fmt="%d-%b-%y"):
        return self.date().strftime(fmt)

    def charge(self, fmt="£%.2f"):
        if self.Hours > 0:
            return fmt % (self.Charge / 100)
        else:
            return "--"

    def hours(self):
        if self.Hours > 0:
            return "%.2f" % (self.Hours/100)
        else:
            return "--"

    def get_total(self):
        if self.Hours > 0:
            total = (self.Charge / 100) * (self.Hours / 100)
        else:
            total = (self.Charge / 100)

        return total

    def get_total_str(self, fmt="£%.2f"):
        return fmt % self.get_total()

    @classmethod
    def from_query(cls, **kwargs):

        query = session().query(OneOff)

        if all(key in kwargs for key in ["day", "month", "year"]):
            try:
                date_to_search = datetime(
                    day=kwargs['day'],
                    month=kwargs['month'],
                    year=kwargs['year'],
                    hour=12).timestamp()
                query = query.filter(OneOff.Date == date_to_search)

            except OverflowError:
                get_module_logger().error(
                    "Could not convert to datetime: %s, %s, %s", str(kwargs['day']), str(kwargs['month']), str(kwargs['year']))
                raise

        else:
            try:
                query = query.filter(OneOff.Date == kwargs['Date'])
            except KeyError:
                pass
        try:
            query = query.filter(OneOff.ClientID ==  kwargs['ClientID'])
        except KeyError:
            pass

        try:
            query = query.filter(OneOff.NumericID ==  kwargs['NumericID'])
        except KeyError:
            pass

        return query

    @classmethod
    def from_id_date_num(cls, ClientID, day, month, year, num):

        year=int(year)
        if year < 100:
            year += 2000
        date_to_match = datetime(day=int(day), month=month_number(month), year=year, hour=12, tzinfo=timezone.utc).timestamp()

        oneoff = cls.from_query(Date=date_to_match, NumericID=num, ClientID=ClientID).all()
        assert len(oneoff) == 1
        return oneoff[0]

    @classmethod
    def get_from_client_id_date(cls, ClientID, timestamp, num):

        date = datetime.fromtimestamp(timestamp)
        oneoff = cls.from_query(day=date.day, month=date.month, year=date.year, NumericID=num, ClientID=ClientID).all()
        assert len(oneoff) == 1
        return oneoff[0]

    @classmethod
    def get_all_for_client(cls, ClientID):
        return cls.from_query(ClientID=ClientID).all()

    @classmethod
    def get_all(cls):
        return cls.from_query().all()

    @staticmethod
    def insert(Name, ClientID, Charge, Hours, Date):
        all_previous = OneOff.from_query(ClientID=ClientID, Date=Date)

        get_module_logger().info("Got %d previous oneoffs for %s on %d", all_previous.count(), ClientID, Date)
        if all_previous.count() > 0:
            new_id = max([oneoff.NumericID for oneoff in all_previous.all()]) + 1
        else:
            new_id = 1

        new_oneoff = OneOff(
            Name=Name,
            ClientID=ClientID,
            Charge=Charge,
            Hours=Hours,
            Date=Date,
            NumericID=new_id,
            State=0)

        session().add(new_oneoff)
        session().commit()
