"""
job_controller.py
"""

import logging

from time import mktime
from datetime import datetime
from calendar import monthrange

from TimeTracker.controllers.invoice_controller import Invoice
from TimeTracker.display_helper import get_sort_key

from TimeTracker.db import db

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

class Job(db.Model):

    __tablename__ = "Jobs"

    Name = db.Column(db.String, primary_key=True)
    ClientID = db.Column(db.String, db.ForeignKey("Clients.ClientID"), primary_key=True)
    DefaultRate = db.Column(db.Integer)
    Active = db.Column(db.Boolean)

    def __str__(self):
        return "{} for client {} at {} p.{}. ({})".format(self.Name, self.ClientID, self.DefaultRate, "Active" if self.Active else "Inactive")

    @classmethod
    def from_name(cls, job_name):
        query = cls.query
        query = query.filter(Job.Name == job_name)
        return query.one()

    def set_active(self, active):
        self.Active = active
        db.session().commit()

    def default_rate(self, fmt="£%.2f"):
        return fmt % (self.DefaultRate/100)

    @staticmethod
    def get_client_id(job_name):
        query = Job.query
        query = query.filter(Job.Name == job_name)
        return query.one().ClientID

    @classmethod
    def get_all_for_client(cls, ClientID):
        query = cls.query
        query = query.filter(Job.ClientID == ClientID)
        return query.all()

    @classmethod
    def get_count_for_client(cls, ClientID):
        return len(cls.get_all_for_client(ClientID))
        
    @classmethod
    def get_active_for_client(cls, ClientID):
        query = cls.query
        query = query.filter(Job.ClientID == ClientID)
        query = query.filter(Job.Active == True)
        return query.all()

    @classmethod
    def get_all_active(cls):
        query = cls.query
        query = query.filter(Job.Active == True)
        return query.all()

    @classmethod
    def get_all(cls):
        query = cls.query
        return query.all()

    @classmethod
    def count(cls):
        return len(cls.get_all())
        
    @staticmethod
    def get_default_rate_for_job(job_name):

        query = Job.query
        query = query.filter(Job.Name == job_name)
        return query.one().DefaultRate / 100

    def insert(self):
        db.session().add(self)
        db.session().commit()
