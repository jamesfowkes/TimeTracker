"""
oneoff_controller.py
"""

import logging

from flask import url_for

from time import mktime
from datetime import datetime, timezone
from calendar import monthrange

from TimeTracker.controllers.invoice_controller import Invoice
from TimeTracker.display_helper import get_sort_key

from TimeTracker.db import db

from TimeTracker.utility import month_number

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

def tuple_to_date(t):
    try:
        (y, m, d) = (int(t[0]), int(t[1]), int(t[2]))
    except ValueError:
        (y, m, d) = (int(t[0]), month_number(t[1]), int(t[2]))
    
    if y < 100:
        y += 2000
    
    return "{}-{:02d}-{:02d}".format(y, m, d)

class OneOff(Invoice, db.Model):

    __tablename__ = "OneOffs"

    Name = db.Column(db.String)
    ClientID = db.Column(db.String, db.ForeignKey("Clients.ClientID"), primary_key=True)
    Charge = db.Column(db.Integer)
    Hours = db.Column(db.Integer)
    Date = db.Column(db.String, primary_key=True)
    State = db.Column(db.Integer)
    NumericID = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return "<OneOff(name='%s', ClientID='%s', charge='%d', hours='%d', date='%d', State='%d', NumericID='%d')>" % (
            self.Name, self.ClientID, self.Charge, self.Hours, self.Date, self.State, self.NumericID)

    def set_state(self, State):
        self.State = self.get_possible_states().index(State)

        get_module_logger().info("New State = %d", self.State)

        db.session().commit()

    def get_state(self):
        return self.State

    def num(self):
        return self.NumericID

    def datetime(self):
        return datetime.strptime(self.Date, "%Y-%m-%d")

    def date(self):
        return self.datetime().date()

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

    def type(self):
        "Oneoff Invoice"
    
    def date_identifier(self):
        return "'" + self.format_date("%Y-%m-%d") + "'"

    @classmethod
    def from_query(cls, **kwargs):
        
        query = OneOff.query

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

        return query.order_by(OneOff.Date)

    @classmethod
    def get_from_client_id_between_dates(cls, ClientID, startdate=None, enddate=None):
        if type(startdate) == tuple:
            startdate = tuple_to_date(startdate)

        if type(enddate) == tuple:
            enddate = tuple_to_date(enddate)
        
        if enddate and startdate:
            get_module_logger().info("Querying OneOff for %s from date %s to %s", ClientID, startdate, enddate)
        
        elif startdate:
            get_module_logger().info("Querying OneOff for %s from date %s", ClientID, startdate)

        elif enddate:
            get_module_logger().info("Querying OneOff for %s to date %s", ClientID, enddate)

        query = OneOff.query

        query = query.filter(OneOff.ClientID ==  ClientID)
        
        if startdate:
            query = query.filter(OneOff.Date >= startdate)
        
        if enddate:
            query = query.filter(OneOff.Date <= enddate)
        
        return query.all()

    @classmethod
    def get_from_client_id_date_and_num(cls, ClientID, startdate, num, enddate=None):

        if type(startdate) == tuple:
            startdate = tuple_to_date(startdate)

        get_module_logger().info("Querying OneOff for %s on date %s, number %s", ClientID, startdate, num)

        oneoff = cls.from_query(Date=startdate, NumericID=num, ClientID=ClientID).all()
        assert len(oneoff) == 1
        return oneoff[0]

    @classmethod
    def get_all(cls):
        return cls.from_query().all()

    @staticmethod
    def insert(Name, ClientID, Charge, Hours, Date):
        all_previous = OneOff.from_query(ClientID=ClientID, Date=Date)

        get_module_logger().info("Got %d previous oneoffs for %s on %s", all_previous.count(), ClientID, Date)
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

        db.session().add(new_oneoff)
        db.session().commit()

    @staticmethod
    def delete(Name, ClientID, Date, NumericID):
        
        Date = Date.strftime("%Y-%m-%d")
        get_module_logger().info("Deleting %s for client %s on %s, ID %d", Name, ClientID, Date, NumericID)
        query = OneOff.query
        query = query.filter(OneOff.Name == Name)
        query = query.filter(OneOff.ClientID == ClientID)
        query = query.filter(OneOff.Date == Date)
        query = query.filter(OneOff.NumericID == NumericID)
        db.session().delete(query.one())
        db.session().commit()

    def get_pdf_url(self):
        return url_for('get_oneoff_invoice_as_pdf',
            ClientID=self.ClientID, name=self.Name,
            date=self.datetime().day, month=self.datetime().month, year=self.datetime().year, num=self.NumericID)