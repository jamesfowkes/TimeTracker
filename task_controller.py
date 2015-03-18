"""
task_controller.py
"""

import logging

from time import mktime
from datetime import datetime
from calendar import monthrange

from TimeTracker.invoice_controller import Invoice
from TimeTracker.display_helper import get_sort_key

from TimeTracker.db import session
from TimeTracker.base import Base

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

class Task(Base):

    __tablename__ = "Tasks"

    Job = Column(String, ForeignKey("Jobs.Name"), primary_key=True)
    ClientID = Column(String, ForeignKey("Clients.ClientID"), primary_key=True)
    Description = Column(String, primary_key=True)
    Rate = Column(Integer)
    Start = Column(Integer, primary_key=True)
    Finish = Column(Integer, primary_key=True)

    def table_sort_key(self):
        return get_sort_key(datetime.fromtimestamp(self.Finish))

    def date(self, fmt="%d-%b-%y"):
        return datetime.fromtimestamp(self.Finish).strftime(fmt)

    def rate(self, fmt=None):
        rate = (self.Rate / 100)
        if fmt:
            rate = fmt % rate

        return rate

    def total(self, fmt=None):
        total = self.hours() * (self.Rate / 100)
        if fmt:
            total = fmt % total

        return total

    def start(self, fmt="%H:%M"):
        return datetime.fromtimestamp(self.Start).strftime(fmt)

    def finish(self, fmt="%H:%M"):
        return datetime.fromtimestamp(self.Finish).strftime(fmt)

    def hours(self, fmt = None):
        hours = (self.Finish - self.Start) / 3600

        if fmt:
            hours = fmt % hours

        return hours

    @classmethod
    def get_for_client_in_month(cls, ClientID, year, month):

        year = int(year)
        month = int(month)
        month_start = mktime(datetime(year, month, 1).timetuple())
        days_in_month = monthrange(year, month)[1]
        month_end = mktime(datetime(year, month, days_in_month).timetuple())
        month_end += 86399 # Go up to 23:59 on last day of month

        query = session().query(Task)
        query = query.filter(Task.ClientID == ClientID)
        query = query.filter(Task.Start >= month_start)
        query = query.filter(Task.Start <= month_end)

        return query.all()

    @classmethod
    def get_for_job(cls, job_name):

        query = session().query(Task)
        query = query.filter(Task.Job == job_name)
        query = query.order_by(Task.Start.asc())

        return query.all()

    @staticmethod
    def get_months_when_worked_for_client(ClientID):

        """ Returns a list of datetimes representing the months
        when at least one piece of work was done for the requested
        client
        """

        start_of_current_month = datetime(datetime.now().year, datetime.now().month, 1)

        query = session().query(Task)
        query = query.filter(Task.ClientID == ClientID)
        tasks = query.all()

        #data = select(["Start"], "Tasks", "ClientID='%s'" % ClientID)
        unique_months = set()
        #for row in data:
            #this_row_date = datetime.fromtimestamp(row['Start'])
            #if this_row_date < start_of_current_month: # Only include complete months
            #    start_of_month_date = datetime(this_row_date.year, this_row_date.month, 1)
            #    unique_months.add(start_of_month_date)

        for task in tasks:
            this_task_date = datetime.fromtimestamp(task.Start)
            if this_task_date < start_of_current_month:  # Only include complete months
                start_of_month_date = datetime(this_task_date.year, this_task_date.month, 1)
                unique_months.add(start_of_month_date)

        get_module_logger().info("Got unique months [%s] for client %s",
            ", ".join([month.strftime("%b") for month in unique_months]),
            ClientID)

        return unique_months