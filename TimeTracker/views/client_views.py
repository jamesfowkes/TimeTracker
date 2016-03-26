"""
client_views.py
Handles generating views for client-centric data
"""

from calendar import month_name

import logging

from TimeTracker import app
from TimeTracker.controllers.client_controller import Client
from TimeTracker.controllers.task_controller import Task
from TimeTracker.controllers.oneoff_controller import OneOff
from TimeTracker.controllers.invoice_controller import get_invoice_instance_data

from flask import render_template, request, redirect, url_for, flash
from flask_weasyprint import HTML, render_pdf

from TimeTracker.views.task_views import get_tasks_total_str

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

def get_client_data_for_month_for_render(ClientID, year, month):
    """ Pull the invoice data for this client, year, month and return a
    client, tasks_data, total tuple for rendering """
    client = Client.get(ClientID)
    tasks = Task.get_for_client_in_month(ClientID, year, month)
    total = get_tasks_total_str(tasks)

    get_module_logger().info("Got %d tasks for %s", len(tasks), ClientID)

    return (client, tasks, total)

@app.route("/")
def index():
    """ Default route: displays table of clients """
    return clients()

@app.route("/clients")
def clients():
    """ Displays table of clients """
    entries = Client.get_all()
    return render_template("clients.template.html", page_title="Clients", clients=entries)

@app.route("/clients/add", methods=['POST'])
def add_new_client():
    """ Adds a new client to the database """
    ClientID = request.form['id']
    name = request.form['name']
    address = request.form['address']
    email =  request.form['email']

    if valid_client_id(ClientID):
        address = format_address_for_display(address)
        client = Client(
            ClientID=ClientID,
            Name=name,
            Address=address,
            Email=email)
        client.insert()

    return redirect(url_for('clients'))

def valid_client_id(ClientID):
    """ Client IDs are valid if less than 4 chars, alphanumeric and uppercase. """
    return len(ClientID) <= 3 and ClientID.isalpha() and ClientID.isupper()

def format_address_for_display(address):
    """ Replaces line breaks in client address with HTML breaks """
    return address.replace("\r\n", "<br>")
