"""
invoice_views.py
Handles generating views for invoice data
"""

import logging
import datetime

from collections import namedtuple

from TimeTracker import app

from TimeTracker.controllers.client_controller import Client
from TimeTracker.controllers.monthly_invoice_controller import MonthlyInvoice
from TimeTracker.controllers.oneoff_controller import OneOff

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_weasyprint import HTML, render_pdf

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

Totals = namedtuple("Totals", ["Gross", "Tax", "Net","ToTransfer"])
def get_totals_by_type(invoices):
    return Totals(
        sum(invoice.get_total() for invoice in invoices),
        sum(invoice.get_tax() for invoice in invoices),
        sum(invoice.get_total() - invoice.get_tax() for invoice in invoices),
        sum(invoice.get_tax() for invoice in invoices if invoice.state_string() == "Paid"))

def get_tax_year_for_date(d):
    if d.month < 4:
        return d.year - 1
    if d.month == 4 and d.day <= 5:
        return d.year - 1

    return d.year


def get_tax_year_start(year):
    return datetime.datetime(year=year, month=4, day=6)

def get_tax_year_end(year):
    return datetime.datetime(year=year+1, month=4, day=5)

@app.route("/invoices/<year>")
def render_invoice_for_year(year):
    """ Render a table of invoices for one tax year """

    clients = Client.get_all()

    start_date = get_tax_year_start(int(year))
    end_date = get_tax_year_end(int(year))

    invoices = []
    for client in clients:
        invoices += MonthlyInvoice.get_from_client_id_between_dates(client.ClientID, start_date, end_date)
        invoices += OneOff.get_from_client_id_between_dates(client.ClientID, start_date, end_date)

    invoices.sort()

    totals = get_totals_by_type(invoices)

    get_module_logger().info("Got %d invoices for rendering", len(invoices))

    return render_template("invoices.template.html", invoices=invoices, totals = totals, year={'start':year, 'end':str(int(year)+1)})

@app.route("/invoices")
def render_default_invoice():
    return render_invoice_for_year(str(get_tax_year_for_date(datetime.datetime.now())))

@app.route("/invoices/change_state")
def change_invoice_state():
    
    ClientID = request.args.get('ClientID', "", type=str)
    num =  request.args.get('num', -1, type=int)
    state = request.args.get('state', "", type=str)
    

    if num != -1:
        date = request.args.get('date_identifier', "", type=str)
        invoice = OneOff.get_from_client_id_date_and_num(ClientID, date, num=num)
    else:
        timestamp = request.args.get('date_identifier', 0, type=int)
        invoice = MonthlyInvoice.get_from_client_id_date(ClientID, timestamp)

    result = invoice.set_state(state)

    return jsonify(result=result)