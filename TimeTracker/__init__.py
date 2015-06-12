from flask import Flask

app = Flask(__name__)
app.config.from_envvar("TIMETRACKER_CONFIG")

import TimeTracker.display_helper
import TimeTracker.views.task_views
import TimeTracker.views.job_views
import TimeTracker.views.client_views
import TimeTracker.views.invoice_views

import TimeTracker.db
