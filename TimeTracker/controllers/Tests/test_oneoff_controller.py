import unittest
import tempfile
import os
import datetime

import TimeTracker

from TimeTracker.controllers.oneoff_controller import OneOff
from TimeTracker.db import db

class OneOffTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, TimeTracker.app.config['DATABASE'] = tempfile.mkstemp()
        TimeTracker.app.config['TESTING'] = True
        self.app = TimeTracker.app.test_client()
        db.create()

        OneOff.insert(Name="TestJobName1", ClientID="ABC", Charge=2000,  Hours=3, Date='2014-02-28')
        OneOff.insert(Name="TestJobName1a", ClientID="ABC", Charge=2000,  Hours=3, Date='2014-02-28')
        OneOff.insert(Name="TestJobName2", ClientID="ABC", Charge=2500,  Hours=7, Date='2014-05-30')
        OneOff.insert(Name="TestJobName3", ClientID="ABC", Charge=35000, Hours=0, Date='2014-06-30')
        OneOff.insert(Name="TestJobName4", ClientID="ABC", Charge=1500,  Hours=20, Date='2015-08-31')
        OneOff.insert(Name="TestJobName5", ClientID="DEF", Charge=30000, Hours=0, Date='2015-01-31')
        OneOff.insert(Name="TestJobName6", ClientID="GHI", Charge=2700,  Hours=10, Date='2015-04-30')
        OneOff.insert(Name="TestJobName7", ClientID="JKL", Charge=25000, Hours=0, Date='2015-09-30')

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(TimeTracker.app.config['DATABASE'])

    def test_oneoff_get_all_returns_all_sorted_by_date(self):
        expected = [
            datetime.date(year=2014, month=2, day=28),
            datetime.date(year=2014, month=2, day=28),
            datetime.date(year=2014, month=5, day=30),
            datetime.date(year=2014, month=6, day=30),
            datetime.date(year=2015, month=1, day=31),
            datetime.date(year=2015, month=4, day=30),
            datetime.date(year=2015, month=8, day=31),
            datetime.date(year=2015, month=9, day=30)
        ]

        actual = [oneoff.date() for oneoff in OneOff.get_all()]

        self.assertEqual(expected, actual)

    def test_oneoff_query_for_client(self):

        expected = ["TestJobName1", "TestJobName1a", "TestJobName2", "TestJobName3", "TestJobName4"]

        actual = [oneoff.Name for oneoff in OneOff.get_from_client_id_between_dates("ABC")]

        self.assertEqual(expected, actual)

    def test_oneoff_get_from_client_id_and_numeric_id_and_on_date(self):

        expected = ["TestJobName1", "TestJobName1a"]

        actual = [
            OneOff.get_from_client_id_date_and_num("ABC", "2014-02-28", 1).Name,
            OneOff.get_from_client_id_date_and_num("ABC", "2014-02-28", 2).Name
        ]

        self.assertEqual(expected, actual)
        
        expected = ["TestJobName1", "TestJobName1a"]

        actual = [
            OneOff.get_from_client_id_date_and_num("ABC", ("2014", "02", "28"), 1).Name,
            OneOff.get_from_client_id_date_and_num("ABC", ("2014", "02", "28"), 2).Name
        ]

        self.assertEqual(expected, actual)

    def test_oneoff_get_from_client_id_between_dates(self):
        
        expected = ["TestJobName2", "TestJobName3", "TestJobName4"]

        actual = [job.Name for job in OneOff.get_from_client_id_between_dates("ABC", "2014-05-01", "2015-09-01")]

        self.assertEqual(expected, actual)

        start = datetime.datetime(year=2014, month=5, day=1)
        end = datetime.datetime(year=2015, month=9, day=1)

        actual = [job.Name for job in OneOff.get_from_client_id_between_dates("ABC", start, end)]

        self.assertEqual(expected, actual)

    def test_oneoffs_created_on_same_dates_for_same_client_have_sequential_ids(self):

        OneOff.insert(Name="TestJobName1b", ClientID="ABC", Charge=2000,  Hours=3, Date='2014-02-28')

        expected = [1, 2, 3]

        actual = [oneoff.NumericID for oneoff in OneOff.get_from_client_id_between_dates("ABC")]

if __name__ == "__main__":
    unittest.main()
