import unittest
import datetime

import TimeTracker

from TimeTracker.controllers import trello

class TrelloControllerTestCase(unittest.TestCase):
    
    def test_JobStringIsParsedInDescTimeDateOrder(self):
        test_string = "Test Task, 1000-1500, 2016-04-10"
        result = trello.parse_monthly_job_string("", "", test_string)
        self.assertEqual(result.desc, "Test Task")

    def test_JobStringIsParsedInDescDateTimeOrder(self):
        test_string = "Test Task, 2016-04-10, 1000-1500"
        result = trello.parse_monthly_job_string("", "", test_string)
        self.assertEqual(result.desc, "Test Task")

    def test_JobStringIsParsedInTimeDescDateOrder(self):
        test_string = "1000-1500, Test Task, 2016-04-10"
        result = trello.parse_monthly_job_string("", "", test_string)
        self.assertEqual(result.desc, "Test Task")

    def test_JobStringIsParsedInTimeDateDescOrder(self):
        test_string = "1000-1500, 2016-04-10, Test Task"
        result = trello.parse_monthly_job_string("", "", test_string)
        self.assertEqual(result.desc, "Test Task")

    def test_JobStringIsParsedInDateTimeDescOrder(self):
        test_string = "2016-04-10, 1000-1500, Test Task"
        result = trello.parse_monthly_job_string("", "", test_string)
        self.assertEqual(result.desc, "Test Task")

    def test_JobStringIsParsedInDateDescTimeOrder(self):
        test_string = "2016-04-10, Test Task, 1000-1500"
        result = trello.parse_monthly_job_string("", "", test_string)
        self.assertEqual(result.desc, "Test Task")


    def test_GenerateMonthlyTaskInfo(self):

        result = trello.generate_monthly_task_info("ML", "Example Job", "2016-10-09, Test Task, 0900-1830", lambda v, **kv: None)
        
        self.assertEqual(True, result['result'])
        self.assertEqual("'Test Task' for client ML, job 'Example Job' on 2016-10-09 (0900-1830)", result['text'])
        
if __name__ == "__main__":
    unittest.main()
