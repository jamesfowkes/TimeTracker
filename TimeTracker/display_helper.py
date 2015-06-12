from datetime import date, datetime, timedelta

from TimeTracker import app
from TimeTracker.controllers.client_controller import Client
from TimeTracker.controllers.invoice_controller import Invoice

def get_sort_key(dt):
    #YYYYMMDDHHMMSS sort key for dates
    return dt.strftime("%Y%m%d%H%M%S")

@app.context_processor
def utility_processor():
    def today(fmt):
        return date.today().strftime(fmt)

    return dict(today=today, get_sort_key=get_sort_key, get_all_clients=Client.get_all, get_invoice_states=Invoice.get_possible_states)