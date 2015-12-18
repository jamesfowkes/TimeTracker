"""
invoice_controller.py
"""

import logging

from TimeTracker import app
from TimeTracker.controllers.client_controller import Client

from datetime import datetime


def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

class Invoice:

    @staticmethod
    def get_possible_states():
        return ["Awaiting Payment", "Paid", "Tax Transferred"]

    def set_state(self, state):
        raise NotImplementedError

    def num(self):
        raise NotImplementedError

    def state_string(self):
        return self.get_possible_states()[self.State]

    def get_client_name(self):
        return Client.get(self.ClientID).Name

    def __lt__(self, other):
        return self.datetime() < other.datetime()

    def __gt__(self, other):
        return self.datetime() < other.datetime()

    def __eq__(self, other):
        return self.datetime() == other.datetime()

    def format(self, format):
        return self.datetime().strftime(format)

    def get_total(self):
        raise NotImplementedError

    def get_total_str(self, fmt):
        raise NotImplementedError

    def get_tax(self):
        return (self.get_total() * 0.3)

    def get_tax_str(self, fmt="£%.2f"):
        return fmt % self.get_tax()

    def type(self):
        raise NotImplementedError
        
    @staticmethod
    def table_name():
        raise NotImplementedError

    @staticmethod
    def get_sql_name_list():
        raise NotImplementedError

    @classmethod
    def get_from_client_id_date(cls):
        raise NotImplementedError

    @classmethod
    def get_from_client_id_between_dates(cls):
        raise NotImplementedError
