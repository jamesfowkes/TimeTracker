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

from sqlalchemy import Column, Integer, String, Boolean, func

from TimeTracker.db import select, update

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

class Task:

    def __init__(self, job, ClientID, desc, rate, start, finish):
        self.job = job
        self.ClientID = ClientID
        self.desc = desc
        self._rate = int(rate)
        self._start = int(start)
        self._finish = int(finish)

    def table_sort_key(self):
        return get_sort_key(datetime.fromtimestamp(self._finish))

    def date(self, fmt="%d-%b-%y"):
        return datetime.fromtimestamp(self._finish).strftime(fmt)

    def rate(self, fmt=None):
        rate = (self._rate / 100)
        if fmt:
            rate = fmt % rate

        return rate

    def total(self, fmt=None):
        total = self.hours() * (self._rate / 100)
        if fmt:
            total = fmt % total

        return total

    def start(self, fmt="%H:%M"):
        return datetime.fromtimestamp(self._start).strftime(fmt)

    def finish(self, fmt="%H:%M"):
        return datetime.fromtimestamp(self._finish).strftime(fmt)

    def hours(self, fmt = None):
        hours = (self._finish - self._start) / 3600

        if fmt:
            hours = fmt % hours

        return hours

    @staticmethod
    def get_sql_name_list():
        return ['Job', 'ClientID', 'Description', 'Rate', 'Start', "Finish"]

    @staticmethod
    def table_name():
        return "Tasks"

    @classmethod
    def from_data_dict(cls, data):
        return cls(data['Job'], data['ClientID'], data['Description'], data['Rate'], data['Start'], data['Finish'])

    @classmethod
    def get_for_client_in_month(cls, ClientID, year, month):

        year = int(year)
        month = int(month)
        month_start = mktime(datetime(year, month, 1).timetuple())
        days_in_month = monthrange(year, month)[1]
        month_end = mktime(datetime(year, month, days_in_month).timetuple())
        month_end += 86399 # Go up to 23:59 on last day of month
        entries = select(cls.get_sql_name_list(), cls.table_name(), "ClientID='%s' AND Start >= %d AND Start <= %d" % (ClientID, month_start, month_end))
        return [cls.from_data_dict(entry) for entry in entries]

    @classmethod
    def get_for_job(cls, job_name):
        entries = select(cls.get_sql_name_list(), cls.table_name(), "Job='%s' ORDER BY Start ASC" % job_name)
        return [cls.from_data_dict(entry) for entry in entries]
