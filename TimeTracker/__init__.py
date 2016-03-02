from flask import Flask
from flask_bootstrap import Bootstrap

from TimeTracker.db import add_db

app = Flask(__name__)
app.config.from_envvar("TIMETRACKER_CONFIG")

add_db(app)

Bootstrap(app)

import TimeTracker.display_helper
import TimeTracker.views.task_views
import TimeTracker.views.job_views
import TimeTracker.views.client_views
import TimeTracker.views.invoice_views
