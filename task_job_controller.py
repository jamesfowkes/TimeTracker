"""
task_job_controller.py
"""

import logging

from time import mktime
from datetime import datetime
from calendar import monthrange

from TimeTracker.db import select, update
from TimeTracker.invoice_controller import Invoice
from TimeTracker.display_helper import get_sort_key

def month_lookup(month):
    return datetime.strptime(month, "%b").month

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

class Job:

    def __init__(self, name, ClientID, default_rate, active):
        self.name = name
        self.ClientID = ClientID
        self._default_rate = default_rate
        self.active = active

    def default_rate(self, fmt="£%.2f"):
        return fmt % (self._default_rate/100)

    @classmethod
    def from_data_dict(cls, data):
        return cls(data['Name'], data['ClientID'], data['DefaultRate'], data['Active'])

    @classmethod
    def get_all_for_client(cls, ClientID):
        entries = select(cls.get_sql_name_list(), cls.table_name(), "ClientID='%s'" % ClientID)
        return [cls.from_data_dict(entry) for entry in entries]

    @classmethod
    def get_active_for_client(cls, ClientID):
        entries = select(cls.get_sql_name_list(), cls.table_name(), "ClientID='%s' AND Active=1" % ClientID)
        return [cls.from_data_dict(entry) for entry in entries]

    @classmethod
    def get_all_active(cls):
        entries = select(cls.get_sql_name_list(), cls.table_name(), "Active=1")
        return [cls.from_data_dict(entry) for entry in entries]

    @classmethod
    def get_all(cls):
        entries = select(cls.get_sql_name_list(), cls.table_name(), "")
        return [cls.from_data_dict(entry) for entry in entries]

    @staticmethod
    def get_sql_name_list():
        return ['Name', 'ClientID', 'DefaultRate', 'Active']

    @staticmethod
    def table_name():
        return "Jobs"

    @staticmethod
    def get_default_rate_for_job(job_name):
        rate = select(['DefaultRate'], "Jobs", "Name='%s'" % job_name)[0]['DefaultRate']
        return rate/100

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
