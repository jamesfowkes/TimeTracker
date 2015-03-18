"""
job_controller.py
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

class Job(Base):

    __tablename__ = "Jobs"

    Name = Column(String, primary_key=True)
    ClientID = Column(String, ForeignKey("Clients.ClientID"), primary_key=True)
    DefaultRate = Column(Integer)
    Active = Column(Boolean)

    @classmethod
    def from_name(cls, job_name):
        query = session().query(Job)
        query = query.filter(Job.Name == job_name)
        return query.one()

    def set_active(self, active):
        self.Active = active
        session().commit()

    def default_rate(self, fmt="£%.2f"):
        return fmt % (self.DefaultRate/100)

    @staticmethod
    def get_client_id(job_name):
        query = session().query(Job)
        query = query.filter(Job.Name == job_name)
        return query.one().ClientID

    @classmethod
    def get_all_for_client(cls, ClientID):
        query = session().query(Job)
        query = query.filter(Job.ClientID == ClientID)
        return query.all()

    @classmethod
    def get_active_for_client(cls, ClientID):
        query = session().query(Job)
        query = query.filter(Job.ClientID == ClientID)
        query = query.filter(Job.Active == True)
        return query.all()

    @classmethod
    def get_all_active(cls):
        query = session().query(Job)
        query = query.filter(Job.Active == True)
        return query.all()

    @classmethod
    def get_all(cls):
        query = session().query(Job)
        return query.all()

    @staticmethod
    def get_default_rate_for_job(job_name):

        query = session().query(Job)
        query = query.filter(Job.Name == job_name)
        return query.one().DefaultRate / 100
