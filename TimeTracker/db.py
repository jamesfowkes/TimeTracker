from TimeTracker import app
from flask import g

from datetime import date
from calendar import monthrange
from time import mktime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging
import sqlite3

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def get_module_logger():
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

_session = None

def session():
    return _session

@app.before_request
def before_request():
    connect_db()

@app.teardown_request
def teardown_request(exception):
    if _session is not None:
        _session.close()

def connect_db():
    global _session
    engine = create_engine('sqlite:///tracker.db')
    Session = sessionmaker(bind=engine)
    _session = Session()