"""
monthly_invoice_controller.py
"""

import logging
from datetime import datetime

from TimeTracker import app
from TimeTracker.controllers.client_controller import Client
from TimeTracker.controllers.invoice_controller import Invoice
from TimeTracker.controllers.task_controller import Task
from TimeTracker.controllers.oneoff_controller import OneOff
from TimeTracker.views.task_views import get_tasks_total

from TimeTracker.db import session, Base

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

class MonthlyInvoice(Invoice, Base):

    __tablename__ = "MonthlyInvoices"

    ClientID = Column(String, ForeignKey("Clients.ClientID"), primary_key=True)
    Month = Column(Integer, primary_key=True)
    Year = Column(Integer, primary_key=True)
    State = Column(Integer, primary_key=True, default=0)

    @staticmethod
    def from_query(ClientID, month, year):

        query = session().query(MonthlyInvoice)
        query = query.filter(MonthlyInvoice.ClientID == ClientID)
        query = query.filter(MonthlyInvoice.Month == month)
        query = query.filter(MonthlyInvoice.Year == year)

        try:
            return query.one()
        except:
            if query.count() > 1:
                raise Exception("Expected exactly 0 or 1 invoices to be returned")
            else:
                # Need to create this invoice
                invoice = MonthlyInvoice(
                    ClientID = ClientID,
                    Month = month,
                    Year = year)

                session().add(invoice)
                session().commit()

                return invoice

    def date(self):
        return self.datetime().date()
        
    def datetime(self):
        return datetime(day=1, month=self.Month, year=self.Year)

    def get_state(self):
        return self.State

    def set_state(self, state):
        self.State = self.get_possible_states().index(state)

        get_module_logger().info("New state = %d", self.State)

        session().commit()

    def get_total(self):

        tasks_for_client = Task.get_for_client_in_month(self.ClientID, self.Year, self.Month)
        total = get_tasks_total(tasks_for_client)
        return total

    def get_total_str(self, fmt="£%.2f"):
        return fmt % self.get_total()

    def format(self, format):
        ## Strip day-based formatting from the format string
        format = format.replace("%d", "")
        return self.date().strftime(format)

    @classmethod
    def get_from_client_id_between_dates(cls, ClientID, startdate=None, enddate=None):
        get_module_logger().info("Getting monthly invoices for %s", ClientID)

        unique_months = Task.get_months_when_worked_for_client(ClientID)

        if startdate is not None:
            unique_months = [month for month in unique_months if month >= startdate]

        if enddate is not None:
            unique_months = [month for month in unique_months if month <= enddate]

        invoices = [cls.from_query(ClientID, unique_month.month, unique_month.year) for unique_month in unique_months]

        invoices.sort()

        return invoices

    @classmethod
    def get_from_client_id_date(cls, ClientID, timestamp):
        date = datetime.fromtimestamp(timestamp)
        invoice = cls.from_query(ClientID, date.month, date.year)
        assert invoice is not None
        return invoice

    def date_identifier(self):
        return self.datetime().timestamp()

    def type(self):
        "Monthly Invoice"
    
    @staticmethod
    def num():
        return -1 ## Monthly invoices always return -1 for their ID

    @staticmethod
    def get_sql_name_list():
        return ['ClientID', 'Month', 'Year', 'State']

    @staticmethod
    def table_name():
        return "MonthlyInvoices"
