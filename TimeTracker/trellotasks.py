"""
trellotasks.py
"""

import logging

from datetime import datetime

from trolly.client import Client as TrollyClient
from trolly.board import Board

from TimeTracker import app
from flask import url_for

from urllib.parse import urlencode

from TimeTracker.controllers.client_controller import Client
from TimeTracker.controllers.job_controller import Job

client = TrollyClient(app.config['TRELLO_API_KEY'], app.config['TRELLO_TOKEN'])

def get_module_logger():
    """ Returns the logger for this module """
    return logging.getLogger(__name__)

get_module_logger().setLevel(logging.INFO)

def validate_oneoff_trello_data(data):

	# Check that date can be parsed
	try:
		task_date = datetime.strptime(data['date'], "%Y-%m-%d")
	except:
		return "Invalid date '{}'".format(data['date'])

	return True

def validate_monthly_trello_data(data):

	# Check that date can be parsed
	try:
		task_date = datetime.strptime(data['date'], "%Y-%m-%d")
	except:
		return "Invalid date '{}'".format(data['date'])

	# Check that times can be parsed
	try:
		task_start = datetime.strptime(data['start'], "%H%M")
	except:
		return "Invalid time '{}'".format(data['start'])
	try:
		task_end = datetime.strptime(data['end'], "%H%M")
	except:
		return "Invalid time '{}'".format(data['end'])

	# Check that start is earlier than finish
	if task_start > task_end:
		return "Start time ({}) earlier than end time ({})".format(data['start'], data['end'])

	if task_start == task_end:
		return "Start time equal to end time ({})".format(data['start'])

	return True

def check_token_length(tokens, expected_tokens, original):
	if len(tokens) != expected_tokens:
		return {
			'result':False,
			'error':"Wrong number of tokens (Got {} expected {})".format(len(tokens), expected_tokens),
			'original':original
		}

	return None

def get_times_or_error(time_str):
	times = time_str.split('-')

	if len(times) != 2:
		return {
			'result':False,
			'error':"Time expected in format HHMM-HHMM",
			'original':task_str
		}

	return times

def generate_oneoff_task_info(task_str):

	get_module_logger().info("Parsing {}", task_str)

	tokens = [tok.strip() for tok in task_str.split(',')]

	error = check_token_length(tokens, 5, task_str)
	if error is not None:
		return error

	params = {
		'client_id': tokens[0],
		'job': tokens[1],
		'date': tokens[2],
		'hours': tokens[3],
		'rate': tokens[4]
	}

	result = validate_oneoff_trello_data(params)

	if result != True:
		return {'result':False, 'error': result, 'original':task_str}

	url = url_for('add_oneoff_task_from_trello_data', **params)
	text = "'{}' for client {} on {} ({} hours at £{:.2f})".format(
		params['job'], params['client_id'], params['date'], params['hours'], float(params['rate']))

	return {'result':True, 'text':text, 'href':url}

def generate_monthly_task_info(client_id, job_name, task_str):

	tokens = [tok.strip() for tok in task_str.split(',')]

	error = check_token_length(tokens, 3, task_str)
	if error is not None:
		return error

	times = get_times_or_error(tokens[1])
	if type(times) == dict:
		return error

	params = {
		'client_id': client_id,
		'job': job_name,
		'date': tokens[0],
		'start': times[0],
		'end': times[1],
		'desc': tokens[2]
	}

	result = validate_monthly_trello_data(params)

	if result != True:
		return {'result':False, 'error': result, 'original':task_str}

	url = url_for('add_monthly_task_from_trello_data', **params)
	text = "'{}' for client {}, job '{}' on {} ({}-{})".format(
		params['desc'], params['client_id'], params['job'], params['date'], params['start'], params['end'])

	return {'result':True, 'text':text, 'href':url}

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
				'original': task_list.name
			}
	except:
		return {
			'result': False,
			'error': "No job '{}'".format(job_name),
			'original': task_list.name
		}

	return True

def get_tasks():
	board = Board(client, 'G1dv6l7l')
	board_lists = board.get_lists()

	tasks = []

	for task_list in board_lists:
		if task_list.name == "Oneoffs":
			# Treat cards in this list as one off jobs with 5 tokens to parse
			for task in task_list.get_cards():
				task_dict = generate_oneoff_task_info(task.get_card_information()['name'])
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
				task_dict = generate_monthly_task_info(client_id, job_name, task.get_card_information()['name'])
				tasks.append( task_dict )


	return tasks
