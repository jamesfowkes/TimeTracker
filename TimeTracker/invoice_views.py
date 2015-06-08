"""
invoice_views.py
Handles generating views for invoice data
"""


import logging

from collections import namedtuple

from TimeTracker import app

from TimeTracker.client_controller import Client
from TimeTracker.monthly_invoice_controller import MonthlyInvoice
from TimeTracker.oneoff_controller import OneOff

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_weasyprint import HTML, render_pdf

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

@app.route("/invoices")
def invoices():
    """ Render a table of all invoices """

    clients = Client.get_all()

    invoices = []
    for client in clients:
        invoices += MonthlyInvoice.get_all_for_client(client.ClientID)
        invoices += OneOff.get_all_for_client(client.ClientID)

    invoices.sort()

    Totals = namedtuple("Totals", ["Gross", "Tax", "Net"])
    totals = Totals(
        sum(invoice.get_total() for invoice in invoices),
        sum(invoice.get_tax() for invoice in invoices),
        sum(invoice.get_total() - invoice.get_tax() for invoice in invoices))

    get_module_logger().info("Got %d invoices for rendering", len(invoices))

    return render_template("invoices.template.html", invoices=invoices, totals = totals)

@app.route("/invoices/change_state")
def change_invoice_state():
    ClientID = request.args.get('ClientID', "", type=str)
    timestamp = request.args.get('timestamp', 0, type=int)
    state = request.args.get('state', "", type=str)
    num =  request.args.get('num', -1, type=int)

    if num != -1:
        invoice = OneOff.get_from_client_id_date(ClientID, timestamp, num=num)
    else:
        invoice = MonthlyInvoice.get_from_client_id_date(ClientID, timestamp)

    result = invoice.set_state(state)

    return jsonify(result=result)