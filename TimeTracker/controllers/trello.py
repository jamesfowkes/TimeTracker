"""
trello.py
"""

import logging
import re

from datetime import datetime

from collections import namedtuple

from trolly.client import Client as TrollyClient
from trolly.board import Board

from TimeTracker import app
from flask import url_for

from urllib.parse import urlencode

from TimeTracker.controllers.client_controller import Client
from TimeTracker.controllers.job_controller import Job

client = TrollyClient(app.config['TRELLO_API_KEY'], app.config['TRELLO_TOKEN'])

class MonthlyTask:

    def __init__(self, client_id, job, desc, start, end, date):
        self.client_id = client_id
        self.job = job
        self.desc = desc
        self.start = start
        self.end = end
        self.date = date

    def to_dict(self):
        return {
            'client_id': self.client_id,
            'job': self.job,
            'desc': self.desc,
            'start': self.start,
            'end': self.end,
            'date': self.date
        } 

    def text(self):
        return "'{}' for client {}, job '{}' on {} ({}-{})".format(self.desc, self.client_id, self.job, self.date,self.start, self.end)

    def validate(self):

        # Check that date can be parsed
        try:
            task_date = datetime.strptime(self.date, "%Y-%m-%d")
        except:
            return "Invalid date '{}'".format(self.date)

        # Check that times can be parsed
        try:
            task_start = datetime.strptime(self.start, "%H%M")
        except:
            return "Invalid time '{}'".format(self.start)
        try:
            task_end = datetime.strptime(self.end, "%H%M")
        except:
            return "Invalid time '{}'".format(self.end)

        # Check that start is earlier than finish
        if task_start > task_end:
            return "Start time ({}) earlier than end time ({})".format(self.start, self.end)

        if task_start == task_end:
            return "Start time equal to end time ({})".format(self.start)

        return None

class OneOffTask:

    def __init__(self, client_id, job, date, hours, rate):
        self.client_id = client_id
        self.job = job
        self.date = date
        self.hours = hours
        self.rate = rate

    def to_dict(self):
        return {
            'client_id': self.client_id,
            'job': self.job,
            'date': self.date,
            'hours': self.hours,
            'rate': self.rate,
        }

    def validate(self):
        try:
            task_date = datetime.strptime(self.date, "%Y-%m-%d")
        except:
            return "Invalid date '{}'".format(self.date)

        return None

    def text(self):
        return "'{}' for client {} on {} ({} hours at £{:.2f})".format(
            self.job, self.client_id, self.date, self.hours, float(self.rate))

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

def try_parse_for_description(tok):
    if tok and not tok[0:3].isnumeric():
        return tok

def try_parse_for_date(tok):
    
    r = re.compile("\d{4}-\d{2}-\d{2}")
    if r.match(tok) is not None:
        return tok

def try_parse_for_times(tok):
    if tok and len(tok) == 9 and tok[4] == "-":
        return tok[0:4], tok[5:9]

    return None, None

def get_date_from_tokens(tokens):
    
    date = None
    for tok in tokens:
        date = date or try_parse_for_date(tok)
    return date

def get_times_from_tokens(tokens):

    start, end = None, None
    for tok in tokens:
        if not start and not end:
            start, end = try_parse_for_times(tok)
    return start, end

def get_description_from_tokens(tokens):

    desc = None
    for tok in tokens:
        desc = desc or try_parse_for_description(tok)
    return desc

def check_token_length(tokens, expected_tokens, original):
    if len(tokens) != expected_tokens:
        return {
            'result':False,
            'error':"Wrong number of tokens (Got {} expected {})".format(len(tokens), expected_tokens),
            'original':original
        }

    return None

def parse_monthly_job_string(client_id, job_name, task_str):
    get_module_logger().info("Parsing {}".format(task_str))

    tokens = [tok.strip() for tok in task_str.split(',')]

    start, end = get_times_from_tokens(tokens)
    task_date = get_date_from_tokens(tokens)
    desc = get_description_from_tokens(tokens)

    if start and end and task_date and desc:
        return MonthlyTask(client_id, job_name, desc, start, end, task_date)

def parse_oneoff_task_string(task_str):
    tokens = [tok.strip() for tok in task_str.split(',')]

    error = check_token_length(tokens, 5, task_str)
    if error is None:
        task = OneOffTask(*tokens)
    else:
        task = None

    return task, error

def get_times_or_error(time_str):
    times = time_str.split('-')

    if len(times) != 2:
        return {
            'result':False,
            'error':"Time expected in format HHMM-HHMM",
            'original':time_str
        }

    return times

def generate_oneoff_task_info(task_str, url_processor):

    get_module_logger().info("Parsing '{}' as oneoff task".format(task_str))

    task, create_error = parse_oneoff_task_string(task_str)

    if create_error is None:
        validate_error = task.validate()

        if validate_error:
            return {'result':False, 'error': validate_error, 'original':task_str}
    else:
        return {'result':False, 'error': create_error, 'original':task_str}

    url = url_processor('add_oneoff_task_from_trello_data', **task.to_dict())

    return {'result':True, 'text':task.text(), 'href':url}

def generate_monthly_task_info(client_id, job_name, task_str, url_processor):

    get_module_logger().info("Parsing {} for {} in job {}".format(task_str, client_id, job_name))
    
    task = parse_monthly_job_string(client_id, job_name, task_str)
    validate_error = task.validate()

    if validate_error:
        return {'result':False, 'error': validate_error, 'original':task_str}

    url = url_processor('add_monthly_task_from_trello_data', **task.to_dict())

    return {'result':True, 'text':task.text(), 'href':url}

def get_client_id_and_job(name):
    split_info = [s.strip() for s in name.split("-")]
    return split_info[0], split_info[1]

def check_client_id_exists_or_error(client_id, err_list, original):
    # Check that client ID exists in database
    try:
        Client.get(client_id)
    except:
        return {
            'result': False,
            'error': "No client ID '{}'".format(client_id),
            'original': original
        }

    return True

def check_job_name_exists_or_error(client_id, job_name, err_list, original):
    # Check that job exists in database
    try:
        job = Job.from_name(job_name)
        if job.ClientID != client_id:
            return {
                'result': False,
                'error': "No job '{}' for client {}".format(job_name, client_id),
                'original': original
            }
    except:
        return {
            'result': False,
            'error': "No job '{}'".format(job_name),
            'original': original
        }

    return True

def get_tasks(url_processor):
    board = Board(client, 'G1dv6l7l')
    board_lists = board.get_lists()

    tasks = []

    for task_list in board_lists:
        if task_list.name == "Oneoffs":
            # Treat cards in this list as one off jobs with 5 tokens to parse
            for task in task_list.get_cards():
                task_dict = generate_oneoff_task_info(task.get_card_information()['name'], url_processor)
                tasks.append( task_dict )
        else:
            # Treat cards in this list as monthly jobs with 3 tokens to parse
            try:
                client_id, job_name = get_client_id_and_job(task_list.name)
            except:
                tasks.append(
                    {
                        'result': False,
                        'error': "Could not parse board name into client ID and job name",
                        'original': task_list.name
                    }
                )
                continue


            result = check_client_id_exists_or_error(client_id, tasks, task_list.name)
            if type(result) == dict:
                tasks.append(result)
                continue

            result = check_job_name_exists_or_error(client_id, job_name, tasks, task_list.name)
            if type(result) == dict:
                tasks.append(result)
                continue

            for task in task_list.get_cards():
                task_dict = generate_monthly_task_info(client_id, job_name, task.get_card_information()['name'], url_processor)
                tasks.append( task_dict )


    return tasks
