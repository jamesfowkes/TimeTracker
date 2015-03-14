from flask import Flask

app = Flask(__name__)

import TimeTracker.display_helper
import TimeTracker.task_views
import TimeTracker.job_views
import TimeTracker.client_views
import TimeTracker.invoice_views

import TimeTracker.db
