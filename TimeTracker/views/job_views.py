"""
job_views.py
"""

import logging

from datetime import datetime, timezone
from TimeTracker import app
from TimeTracker.controllers.client_controller import Client
from TimeTracker.controllers.monthly_invoice_controller import MonthlyInvoice
from TimeTracker.controllers.job_controller import Job
from TimeTracker.controllers.oneoff_controller import OneOff
from TimeTracker import trellotasks

from flask import render_template, request, redirect, url_for, flash, g

from TimeTracker.views.task_views import tasks_for_client_job

def add_trello_task_links_to_g():
    g.tasks_to_add = trellotasks.get_tasks()

class JobView:

    """ Container class to pass to template """
    def __init__(self, client, jobs, oneoffs, active_only, client_has_jobs):
        self.client = client
        self.jobs = jobs
        self.oneoffs = oneoffs
        self.active_only = active_only
        self.client_has_jobs = client_has_jobs

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

    oneoffs = OneOff.get_from_client_id_between_dates(ClientID)

    invoices = MonthlyInvoice.get_from_client_id_between_dates(ClientID)

    job = JobView(client, jobs, oneoffs, False, Job.get_count_for_client(ClientID) > 0)

    add_trello_task_links_to_g()

    return render_template("jobs.template.html", page_title="Jobs", job_info=job, invoices=invoices)

@app.route("/jobs/<ClientID>/active")
def active_jobs_for_client(ClientID):

    """ Displays all the active jobs for a client """

    client = Client.get(ClientID)

    jobs = Job.get_active_for_client(ClientID)

    oneoffs = OneOff.get_from_client_id_between_dates(ClientID)

    invoices = MonthlyInvoice.get_from_client_id_between_dates(ClientID)

    job = JobView(client, jobs, oneoffs, True, Job.get_count_for_client(ClientID) > 0)

    add_trello_task_links_to_g()

    return render_template("jobs.template.html", page_title="Jobs", job_info=job, invoices=invoices)

@app.route("/jobs/active")
def active_jobs():

    """ Displays all the active jobs for all clients """

    jobs = Job.get_all_active()
    oneoffs = OneOff.get_all()

    job = JobView(None, jobs, oneoffs, True, Job.count() > 0)

    add_trello_task_links_to_g()

    return render_template("jobs.template.html", page_title="Jobs", job_info=job)

@app.route("/jobs/all")
def all_jobs():

    """ Displays all jobs for all clients """

    jobs = Job.get_all()

    oneoffs = OneOff.get_all()

    job = JobView(None, jobs, oneoffs, False, Job.count() > 0)

    add_trello_task_links_to_g()

    return render_template("jobs.template.html", page_title="Jobs", job_info=job)

@app.route("/jobs/add", methods=['POST'])
def add_new_job():
    """ Adds a new job to the database """
    ClientID = request.form['ClientID']
    job_name = request.form['job_name']
    rate = int(float(request.form['rate']) * 100)
    client = Client.get(ClientID)

    job = Job(Name=job_name, ClientID=ClientID, DefaultRate=rate, Active=True)
    job.insert()

    return redirect(url_for('all_jobs_for_client', ClientID=ClientID))

@app.route("/jobs/add/oneoff", methods=['POST'])
def add_new_oneoff():
    """ Adds a new oneoff job to the database """
    ClientID = request.form['ClientID']
    oneoff_name = request.form['oneoff_name']
    charge = int(float(request.form['charge']) * 100)
    hours = int(float(request.form['hours']) * 100)
    workdate = request.form['workdate']
    
    OneOff.insert(oneoff_name, ClientID, charge, hours, workdate)

    return redirect(url_for('all_jobs_for_client', ClientID=ClientID))

@app.route("/jobs/<job_name>")
def job(job_name):
    """ Display a job when the client ID is not known """
    ClientID = Job.get_client_id(job_name)
    return tasks_for_client_job(ClientID, job_name)

@app.route("/jobs/<job_name>/activate")
def activate_job(job_name):
    """ Activate a job so it appears in the active list (client ID not known) """
    job = Job.from_name(job_name)
    job.set_active(True)
    return redirect(url_for('all_jobs_for_client', ClientID=job.ClientID))

@app.route("/jobs/<job_name>/deactivate")
def deactivate_job(job_name):
    """ Deactivate a job so it does not appear in the active list (client ID not known) """
    job = Job.from_name(job_name)
    job.set_active(False)
    return redirect(url_for('active_jobs_for_client', ClientID=job.ClientID))

@app.route("/tasks/trello_add_oneoff/<client_id>/<job>/<date>/<hours>/<rate>/")
def add_oneoff_task_from_trello_data(client_id, job, date, hours, rate):
    workdate = datetime.strptime(date, "%Y-%m-%d").timestamp()

    OneOff.insert(job, client_id, int(rate)*100, float(hours) * 100, workdate)

    return redirect(url_for('all_jobs_for_client', ClientID=client_id))