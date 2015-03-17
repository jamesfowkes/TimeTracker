"""
job_views.py
"""

import logging

from datetime import datetime
from TimeTracker import app
from TimeTracker.db import select, insert, update, DBError
from TimeTracker.client_controller import Client
from TimeTracker.monthly_invoice_controller import MonthlyInvoice
from TimeTracker.job_controller import Job
from TimeTracker.oneoff_controller import OneOff

from flask import render_template, request, redirect, url_for, flash

from TimeTracker.task_views import tasks_for_client_job

class JobView:

    """ Container class to pass to template """
    def __init__(self, client, jobs, oneoffs, active_only):
        self.client = client
        self.jobs = jobs
        self.oneoffs = oneoffs
        self.active_only = active_only

    @property
    def title(self):

        title = ""

        if len(self.jobs):
            if self.active_only:
                title = "Active Jobs"
            else:
                title = "All Jobs"

            if self.client is not None:
                    title += " for %s" % self.client.Name

        return title

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

@app.route("/jobs/<ClientID>/all")
def all_jobs_for_client(ClientID):

    """ Displays a all jobs for a client """

    client = Client.get(ClientID)

    jobs = Job.get_all_for_client(ClientID)

    oneoffs = OneOff.get_all_for_client(ClientID)

    invoices = MonthlyInvoice.get_all_for_client(ClientID)

    job = JobView(client, jobs, oneoffs, False)

    return render_template("jobs.template.html", page_title="Jobs", job_info=job, invoices=invoices)

@app.route("/jobs/<ClientID>/active")
def active_jobs_for_client(ClientID):

    """ Displays all the active jobs for a client """

    client = Client.get(ClientID)

    jobs = Job.get_active_for_client(ClientID)

    oneoffs = OneOff.get_all_for_client(ClientID)

    invoices = MonthlyInvoice.get_all_for_client(ClientID)

    job = JobView(client, jobs, oneoffs, True)

    return render_template("jobs.template.html", page_title="Jobs", job_info=job, invoices=invoices)

@app.route("/jobs/active")
def active_jobs():

    """ Displays all the active jobs for all clients """

    jobs = Job.get_all_active()
    oneoffs = OneOff.get_all()

    job = JobView(None, jobs, oneoffs, True)

    return render_template("jobs.template.html", page_title="Jobs", job_info=job)

@app.route("/jobs/all")
def all_jobs():

    """ Displays all jobs for all clients """

    jobs = Job.get_all()

    oneoffs = OneOff.get_all()

    job = JobView(None, jobs, oneoffs, False)

    return render_template("jobs.template.html", page_title="Jobs", job_info=job)

@app.route("/jobs/add", methods=['POST'])
def add_new_job():
    """ Adds a new job to the database """
    ClientID = request.form['ClientID']
    job_name = request.form['job_name']
    rate = int(float(request.form['rate']) * 100)
    client = Client.get(ClientID)

    try:
        insert("jobs", [job_name, ClientID, rate, True])
    except DBError as err:
        flash("Job '%s' for %s could not be added (%s)" % (job_name, client.Name, err.msg))

    return redirect(url_for('all_jobs_for_client', ClientID=ClientID))

@app.route("/jobs/add/oneoff", methods=['POST'])
def add_new_oneoff():
    """ Adds a new oneoff job to the database """
    ClientID = request.form['ClientID']
    oneoff_name = request.form['oneoff_name']
    charge = int(float(request.form['charge']) * 100)
    hours = int(float(request.form['hours']) * 100)
    workdate = datetime.strptime(request.form['workdate'], "%Y-%m-%d").timestamp() + (12*60*60) # Make sure date is in middle of day (avoids messy summertime issues)
    client = Client.get(ClientID)

    try:
        OneOff.Create(oneoff_name, ClientID, charge, hours, workdate)
        #insert("oneoffs", [oneoff_name, ClientID, charge, hours, workdate, 0])
    except DBError as err:
        flash("Job '%s' for %s could not be added (%s)" % (oneoff_name, client.Name, err.msg))

    return redirect(url_for('all_jobs_for_client', ClientID=ClientID))

@app.route("/jobs/<job_name>")
def job(job_name):
    """ Display a job when the client ID is not known """
    ClientID = Job.get_client_id(job_name)
    return tasks_for_client_job(ClientID, job_name)

@app.route("/jobs/<job_name>/activate")
def activate_job(job_name):
    """ Activate a job so it appears in the active list (client ID not known) """
    ClientID = Job.get_client_id(job_name)
    update("jobs", ["Active"], [1], ["ClientID", "Name"], [ClientID, job_name])
    return redirect(url_for('all_jobs', ClientID=ClientID))

@app.route("/jobs/<job_name>/deactivate")
def deactivate_job(job_name):
    """ Deactivate a job so it does not appear in the active list (client ID not known) """
    ClientID = Job.get_client_id(job_name)
    update("jobs", ["Active"], [0], ["ClientID", "Name"], [ClientID, job_name])
    return redirect(url_for('active_jobs', ClientID=ClientID))