import unittest
import tempfile
import os

import TimeTracker

from TimeTracker.controllers.job_controller import Job
from TimeTracker import db

class JobControllerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, TimeTracker.app.config['DATABASE'] = tempfile.mkstemp()
        TimeTracker.app.config['TESTING'] = True
        self.app = TimeTracker.app.test_client()
        db.create()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(TimeTracker.app.config['DATABASE'])

    def test_JobInsertWritesToDatabase(self):
        with TimeTracker.app.test_request_context("/"):
            TimeTracker.app.preprocess_request()

            job = Job(Name="TestJobName", ClientID="ABC", DefaultRate=20.00, Active=True)
            job.insert()
            self.assertEqual(1, Job.count())
if __name__ == "__main__":
    unittest.main()
