from flask.ext.sqlalchemy import SQLAlchemy

db = None

def add_db(app):

    global db
    if "SQLALCHEMY_DATABASE_URI" not in app.config:
        try:
            app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE"] or app.config["DATABASE_URI"]
        except:
            raise Exception("Application configuration must specify DATABASE or DATABASE_URI")
            
    db = SQLAlchemy(app)