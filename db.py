from TimeTracker import app
from flask import g

from datetime import date
from calendar import monthrange
from time import mktime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging
import sqlite3

class DBError(Exception):
    def __init__(self, msg):
        self.msg = msg

def get_module_logger():
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

_engine = None
_connection = None
_session = None

def session():
    return _session

def insert(table, data):
    sql = "INSERT INTO %s VALUES (%s);" % (table, ",".join(["?"] * len(data)))

    get_module_logger().info("Running %s", sql)

    try:
        _connection = g.db.connect()
        g.db.execute(sql, data)
        g.db.commit()
    except sqlite3.IntegrityError:
        raise DBError('Request unsuccessful - Database returned integrity error');

def delete(table, where_cols, where_data):
    sql = "DELETE FROM %s WHERE %s" % (table, " AND ".join(["%s='%s'" % (col, data) for (col, data) in zip(where_cols, where_data)]))

    get_module_logger().info("Running %s", sql)

    try:
        _connection = g.db.connect()
        g.db.execute(sql)
        g.db.commit()
    except:
        raise

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if _connection is not None:
        _connection.close()
    if _session is not None:
        _session.close()

def connect_db():
    global _session
    _engine = create_engine('sqlite:///tracker.db')
    Session = sessionmaker(bind=_engine)
    _session = Session()
    return _engine