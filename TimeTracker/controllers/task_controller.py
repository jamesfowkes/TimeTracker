"""
task_controller.py
"""

import logging

from time import mktime
from datetime import datetime
from calendar import monthrange

from TimeTracker.controllers.invoice_controller import Invoice
from TimeTracker.display_helper import get_sort_key

from TimeTracker.db import db

from collections import namedtuple

class TaskCollection(namedtuple("TaskCollection", ["tasks", "total_hours_", "total_amount_"])):

    __slots__ = ()

    def total_hours(self, fmt = None):
        total = self.total_hours_
        if fmt:
            total = fmt % total

        return total

    def total_amount(self, fmt = None):
        total = self.total_amount_
        if fmt:
            total = fmt % total

        return total

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

class Task(db.Model):

    __tablename__ = "Tasks"

    Job = db.Column(db.String, db.ForeignKey("Jobs.Name"), primary_key=True)
    ClientID = db.Column(db.String, db.ForeignKey("Clients.ClientID"), primary_key=True)
    Description = db.Column(db.String, primary_key=True)
    Rate = db.Column(db.Integer)
    Start = db.Column(db.Integer, primary_key=True)
    Finish = db.Column(db.Integer, primary_key=True)

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

        query = Task.query
        query = query.filter(Task.ClientID == ClientID)
        query = query.filter(Task.Start >= month_start)
        query = query.filter(Task.Start <= month_end)

        return query.all()

    @staticmethod
    def get_for_job(job_name):

        query = Task.query
        query = query.filter(Task.Job == job_name)
        query = query.order_by(Task.Start.asc())

        tasks = query.all()
        total_hours = sum([task.hours() for task in tasks])
        total_amount = sum([task.total() for task in tasks])

        return TaskCollection(tasks, total_hours, total_amount)

    @staticmethod
    def get_months_when_worked_for_client(ClientID):

        """ Returns a list of datetimes representing the months
        when at least one piece of work was done for the requested
        client
        """

        start_of_current_month = datetime(datetime.now().year, datetime.now().month, 1)

        query = Task.query
        query = query.filter(Task.ClientID == ClientID)
        tasks = query.all()

        unique_months = set()

        for task in tasks:
            this_task_date = datetime.fromtimestamp(task.Start)
            if this_task_date < start_of_current_month:  # Only include complete months
                start_of_month_date = datetime(this_task_date.year, this_task_date.month, 1)
                unique_months.add(start_of_month_date)

        get_module_logger().info("Got unique months [%s] for client %s",
            ", ".join([month.strftime("%Y-%b") for month in unique_months]),
            ClientID)

        return unique_months

    def insert(self):
        db.session().add(self)
        db.session().commit()

    @staticmethod
    def delete(Job, ClientID, Description, Start, Finish):

        query = Task.query
        query = query.filter(Task.Job == Job)
        query = query.filter(Task.ClientID == ClientID)
        query = query.filter(Task.Description == Description)
        query = query.filter(Task.Start == Start)
        query = query.filter(Task.Finish == Finish)
        db.session().delete(query.one())
        db.session().commit()