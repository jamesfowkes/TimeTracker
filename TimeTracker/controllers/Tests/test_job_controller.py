import unittest
import tempfile
import os

import TimeTracker

from TimeTracker.controllers.job_controller import Job
from TimeTracker.db import db

class JobControllerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, TimeTracker.app.config['DATABASE'] = tempfile.mkstemp()
        TimeTracker.app.config['TESTING'] = True
        self.app = TimeTracker.app.test_client()
        db.create()

        Job(Name="TestJobName1", ClientID="ABC", DefaultRate=2000, Active=True).insert()
        Job(Name="TestJobName2", ClientID="ABC", DefaultRate=2500, Active=False).insert()
        Job(Name="TestJobName3", ClientID="ABC", DefaultRate=3000, Active=True).insert()
        Job(Name="TestJobName4", ClientID="ABC", DefaultRate=1500, Active=True).insert()
        Job(Name="TestJobName5", ClientID="DEF", DefaultRate=2300, Active=False).insert()
        Job(Name="TestJobName6", ClientID="GHI", DefaultRate=2700, Active=True).insert()
        Job(Name="TestJobName7", ClientID="JKL", DefaultRate=2250, Active=False).insert()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(TimeTracker.app.config['DATABASE'])

    def test_JobGetAll(self):
        with TimeTracker.app.test_request_context("/"):
            TimeTracker.app.preprocess_request()

            jobs = Job.get_all()
            self.assertEqual(7, len(jobs))

    def test_JobGetAllForClient(self):
        with TimeTracker.app.test_request_context("/"):
            TimeTracker.app.preprocess_request()

            jobs_for_abc = Job.get_all_for_client("ABC")
            self.assertEqual(4, len(jobs_for_abc))
            self.assertTrue("TestJobName1" in [job.Name for job in jobs_for_abc])
            self.assertTrue("TestJobName2" in [job.Name for job in jobs_for_abc])
            self.assertTrue("TestJobName3" in [job.Name for job in jobs_for_abc])
            self.assertTrue("TestJobName4" in [job.Name for job in jobs_for_abc])

    def test_JobGetActiveForClient(self):
        with TimeTracker.app.test_request_context("/"):
            TimeTracker.app.preprocess_request()

            active_jobs_for_abc = Job.get_active_for_client("ABC")
            self.assertEqual(3, len(active_jobs_for_abc))
            names = [job.Name for job in active_jobs_for_abc]
            self.assertTrue("TestJobName1" in names)
            self.assertTrue("TestJobName3" in names)
            self.assertTrue("TestJobName4" in names)

    def test_JobGetAllActive(self):
        with TimeTracker.app.test_request_context("/"):
            TimeTracker.app.preprocess_request()

            active_jobs = Job.get_all_active()
            self.assertEqual(4, len(active_jobs))
            names = [job.Name for job in active_jobs]
            self.assertTrue("TestJobName1" in names)
            self.assertTrue("TestJobName3" in names)
            self.assertTrue("TestJobName4" in names)
            self.assertTrue("TestJobName6" in names)

    def test_JobGetDefaultRateReturnsInPounds(self):
        with TimeTracker.app.test_request_context("/"):
            TimeTracker.app.preprocess_request()

            self.assertEqual(20.00, Job.get_default_rate_for_job("TestJobName1"))
            self.assertEqual(22.50, Job.get_default_rate_for_job("TestJobName7"))

if __name__ == "__main__":
    unittest.main()
