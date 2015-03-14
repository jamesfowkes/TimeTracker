"""
client_controller.py
"""

from datetime import datetime

from TimeTracker.db import select

class Client:

    def __init__(self, ClientID, name, address):
        self.id = ClientID
        self.name = name
        self.address = address

    @classmethod
    def get_all(cls):
        all_data = select(['ClientID', 'Name', 'Address'], 'Clients', None)
        return [cls(data['ClientID'], data['Name'], data['Address']) for data in all_data]

    @classmethod
    def get(cls, ClientID):
        data = select(['ClientID', 'Name', 'Address'], 'Clients', "ClientID='%s'" % ClientID)[0]
        return cls(data['ClientID'], data['Name'], data['Address'])

    @classmethod
    def get_for_job(cls, job_name):
        job_data = select(['ClientID'], 'Jobs', "Name='%s'" % job_name)[0]
        return cls.get(job_data['ClientID'])

    @staticmethod
    def get_months_when_worked_for_client(ClientID):

        start_of_current_month = datetime(datetime.now().year, datetime.now().month, 1)

        data = select(["Start"], "Tasks", "ClientID='%s'" % ClientID)
        unique_months = set()
        for row in data:
            this_row_date = datetime.fromtimestamp(row['Start'])
            if this_row_date < start_of_current_month: # Only include complete months
                start_of_month_date = datetime(this_row_date.year, this_row_date.month, 1)
                unique_months.add(start_of_month_date)

        return unique_months