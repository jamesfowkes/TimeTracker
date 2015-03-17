"""
monthly_invoice_controller.py
"""

import logging

from TimeTracker import app
from TimeTracker.db import select, update, insert
from TimeTracker.client_controller import Client
from TimeTracker.invoice_controller import Invoice
from TimeTracker.task_controller import Task
from TimeTracker.oneoff_controller import OneOff
from TimeTracker.task_views import get_tasks_total

from flask import render_template, request, redirect, url_for, flash, jsonify

from datetime import datetime

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

class MonthlyInvoice(Invoice):

    def __init__(self, ClientID, month, year):

        self.try_load_from_db(ClientID, month, year)

    def try_load_from_db(self, ClientID, month, year):

        data = select(self.get_sql_name_list(), self.table_name(), "ClientID='%s' AND Month=%d AND Year=%d" % (ClientID, month, year))
        if len(data) == 1:
            self.State = data[0]['State']
            self.ClientID = data[0]['ClientID']
            self.month = data[0]['Month']
            self.year = data[0]['Year']

        elif len(data) == 0:
            self.create()
        else:
            raise Exception("Expected exactly 0 or 1 invoices to be returned")

    def date(self):
        return datetime(day=1, month=self.month, year=self.year)

    def get_state(self):
        return self.State

    def set_state(self, state):
        self.State = self.get_possible_states().index(State)
        self.State = self.get_possible_states().index(State)

        get_module_logger().info("New state = %d", self.State)

        rowcount = update(self.table_name(), ["State"], [self.State], ["ClientID", "Month", "Year"], [self.ClientID, self.month, self.year])
        assert rowcount == 1

    def get_total(self):

        tasks_for_client = Task.get_for_client_in_month(self.ClientID, self.year, self.month)
        total = get_tasks_total(tasks_for_client)
        return total

    def get_total_str(self, fmt="£%.2f"):
        return fmt % self.get_total()

    def format(self, format):
        ## Strip day-based formatting from the format string
        format = format.replace("%d", "")
        return self.date().strftime(format)

    @classmethod
    def get_all_for_client(cls, ClientID):
        get_module_logger().info("Getting monthly invoices for %s", ClientID)

        unique_months = Client.get_months_when_worked_for_client(ClientID)

        invoices = [cls(ClientID, unique_month.month, unique_month.year) for unique_month in unique_months]

        invoices.sort()

        return invoices

    @classmethod
    def get_from_ClientID_date(cls, ClientID, timestamp):
        date = datetime.fromtimestamp(timestamp)
        invoice = cls(ClientID, date.month, date.year)
        assert invoice is not None
        return invoice

    @staticmethod
    def num():
        return -1 ## Monthly invoices always return -1 for their ID

    @staticmethod
    def get_sql_name_list():
        return ['ClientID', 'Month', 'Year', 'State']

    @staticmethod
    def table_name():
        return "MonthlyInvoices"
