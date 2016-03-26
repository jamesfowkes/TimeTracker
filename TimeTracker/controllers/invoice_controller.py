"""
invoice_controller.py
"""

import logging
import yaml

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
        return ["Awaiting Payment", "Paid"]

    def set_state(self, state):
        raise NotImplementedError

    def num(self):
        raise NotImplementedError

    def state_string(self):
        return self.get_possible_states()[self.State]

    @property
    def client(self):
        return Client.get(self.ClientID)

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

    def get_pdf_url(self):
        raise NotImplementedError

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

def parse_invoice_instance_data(data):

    if 'address' in data:
        data['address'] = data['address'].replace("\n", "<br>")

    if 'payment' in data:
        data['payment_details'] = "{}<br>Account No: {}<br>Sort Code: {}".format(
            data['payment']['name'], data['payment']['accno'], data['payment']['sortcode'])
        
    return data

def get_invoice_instance_data():
    if get_invoice_instance_data.data is None:
        get_invoice_instance_data.data = yaml.load(app.open_instance_resource("invoice-data.yaml", 'r'))

        get_invoice_instance_data.data = parse_invoice_instance_data(get_invoice_instance_data.data)        
        get_module_logger().info("Loaded invoice data: {}".format(get_invoice_instance_data.data))

    return get_invoice_instance_data.data

get_invoice_instance_data.data = None