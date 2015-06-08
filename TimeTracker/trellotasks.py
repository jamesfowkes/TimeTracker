from datetime import datetime

from trolly.client import Client as TrollyClient
from trolly.board import Board

from TimeTracker import app
from flask import url_for

from urllib.parse import urlencode

from TimeTracker.client_controller import Client
from TimeTracker.job_controller import Job

client = TrollyClient(app.config['TRELLO_API_KEY'], app.config['TRELLO_TOKEN'])

def validate_trello_data(data):

	# Check that client ID exists in database
	try:
		Client.get(data['client_id'])
	except:
		return "No client ID '{}'".format(data['client_id'])

	# Check that job exists in database
	try:
		job = Job.from_name(data['job'])
		if job.ClientID != data['client_id']:
			return "No job '{}' for client {}".format(data['job'], data['client_id'])
	except:
		return "No job '{}'".format(data['job'])

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

def generate_add_task_info(task_str):

	tokens = [tok.strip() for tok in task_str.split(',')]
	if len(tokens) != 5:
		return {
			'result':False,
			'error':"Wrong number of tokens (Got {} expected 5)".format(len(tokens)),
			'original':task_str
		}

	times = tokens[3].split('-')

	if len(times) != 2:
		return {
			'result':False,
			'error':"Time expected in format HHMM-HHMM",
			'original':task_str
		}

	params = {
		'client_id': tokens[0],
		'job': tokens[1],
		'date': tokens[2],
		'start': times[0],
		'end': times[1],
		'desc': tokens[4]
	}

	result = validate_trello_data(params)

	if result != True:
		return {'result':False, 'error': result, 'original':task_str}

	url = url_for('add_task_from_trello_data', **params)
	text = "'{}' for client {}, job '{}' on {} ({}-{})".format(
		params['desc'], params['client_id'], params['job'], params['date'], params['start'], params['end'])

	return {'result':True, 'text':text, 'href':url}

def get_tasks():
	board = Board(client, 'G1dv6l7l')
	task_list = board.get_lists()[0]
	
	tasks = []
	for task in task_list.get_cards():
		url = generate_add_task_info(task.get_card_information()['name'])
		tasks.append( url )

	return tasks