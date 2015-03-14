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

def select(cols, frm, where):
    sql = "SELECT %s FROM %s" % (", ".join(cols), frm)
    if where:
        sql += " WHERE %s" % where

    get_module_logger().info("Running %s", sql)

    try:
        cur = g.db.execute(sql)
    except sqlite3.OperationalError:
        get_module_logger().info("Failed with OperationalError")
        raise DBError('Request unsuccessful - Database returned operational error');

    entries = [dict(zip(cols, row)) for row in cur.fetchall()]
    get_module_logger().info("Got %d entries", len(entries))
    return entries

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

def update(table, set_cols, set_data, where_cols, where_data):
    sql = "UPDATE %s SET %s WHERE %s" % (table,
    ", ".join(["%s=%s" % (col, data) for (col, data) in zip(set_cols, set_data)]),
    " AND ".join(["%s='%s'" % (col, data) for (col, data) in zip(where_cols, where_data)])
    )

    get_module_logger().info("Running %s", sql)

    try:
        _connection = g.db.connect()
        cursor = g.db.cursor()
        cursor.execute(sql)
        g.db.commit()
    except:
        raise

    return cursor.rowcount

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