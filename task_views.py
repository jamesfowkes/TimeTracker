"""
task_views.py
Handles generating views for task-centric data
"""

from datetime import datetime, timedelta
from TimeTracker import app
from TimeTracker.db import select, insert, delete, DBError
from TimeTracker.client_controller import Client
from TimeTracker.task_job_controller import Task, Job

from flask import render_template, request, redirect, url_for, flash

@app.route("/tasks/<ClientID>/<job_name>")
def tasks_for_client_job(ClientID, job_name):
    """ Displays all tasks for a given client job """
    default_rate = Job.get_default_rate_for_job(job_name)
    client = Client.get(ClientID)
    tasks = Task.get_for_job(job_name)

    return render_template("tasks.template.html", page_title="Tasks", client=client, job_name=job_name, default_rate=default_rate, tasks=tasks)

@app.route("/tasks/<ClientID>/<job_name>/add", methods=['POST'])
def add_new_task(ClientID, job_name):
    """ Adds a new task for a job """
    desc = request.form['description']
    rate = int(float(request.form['rate']) * 100)
    workdate = datetime.strptime(request.form['workdate'], "%Y-%m-%d")
    start = workdate + timedelta(0, 0, 0, 0, int(request.form['start'][3:5]), int(request.form['start'][0:2]))
    finish = workdate + timedelta(0, 0, 0, 0, int(request.form['finish'][3:5]), int(request.form['finish'][0:2]))

    try:
        insert("tasks", [job_name, ClientID, desc, rate, start.timestamp(), finish.timestamp()])
    except DBError as err:
        flash("Task '%s' on date '%s' could not be added (%s)" % (desc, request.form['workdate'], err.msg))

    return redirect(url_for('tasks_for_client_job', ClientID=ClientID, job_name=job_name))

@app.route("/tasks/<ClientID>/<job_name>/<description>/<date>/<start>/<finish>/delete")
def delete_task(ClientID, job_name, description, date, start, finish):
    """ Deletes a task from a job """
    workdate = datetime.strptime(date, "%d-%b-%y")
    start = workdate + timedelta(0, 0, 0, 0, int(start[3:5]), int(start[0:2]))
    finish = workdate + timedelta(0, 0, 0, 0, int(finish[3:5]), int(finish[0:2]))

    delete(
        "tasks",
        ["Job", "ClientID", "Description", "Start", "Finish"],
        [job_name, ClientID, description, start.timestamp(), finish.timestamp()]
        )

    return redirect(url_for('tasks_for_client_job', ClientID=ClientID, job_name=job_name))

def get_tasks_total(tasks):
    """ Sums (hours*rate) for a list of tasks and returns as decimal """
    return sum([task.total() for task in tasks])

def get_tasks_total_str(tasks, fmt="£%2.2f"):
    """ Sums (hours*rate) for a list of tasks and returns as decimal """
    return fmt % get_tasks_total(tasks)

