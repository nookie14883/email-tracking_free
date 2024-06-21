from flask import Flask, send_from_directory, request, jsonify, Response
import os
from datetime import datetime
import json
from functools import wraps

app = Flask(__name__)

STATIC_FOLDER = 'static'
LOG_FOLDER = 'logs'
LOG_FILE = os.path.join(LOG_FOLDER, 'visits.log')
COUNTER_FILE = os.path.join(LOG_FOLDER, 'counter.log')

os.makedirs(LOG_FOLDER, exist_ok=True)

# Инициализация счетчика
counter = 0
current_date = datetime.now().strftime('%d-%m-%Y')

if os.path.exists(COUNTER_FILE):
	with open(COUNTER_FILE, 'r') as counter_file:
		lines = counter_file.readlines()
		if lines:
			last_line = lines[-1]
			last_date, count = last_line.strip().split(' ')
			if last_date == current_date:
				counter = int(count)


def check_auth(username, password):
	return username == 'lime_checker' and password == 'ldw12fggAgfgh3gG[[vRF'


# Запрос логина и пароля
def authenticate():
	return Response(
		'Could not verify your access level for that URL.\n'
		'You have to login with proper credentials', 401,
		{'WWW-Authenticate':'Basic realm="Login Required"'})


# Декоратор для защиты маршрута
def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)

	return decorated


@app.route('/pixel.png')
def tracking_pixel():
	global counter
	current_date = datetime.now().strftime('%d-%m-%Y')

	try:
		with open(LOG_FILE, 'a') as log_file:
			log_file.write(f"{datetime.now()}, {request.remote_addr}, {request.headers.get('User-Agent')}\n")

		counter += 1

		updated_lines = []
		if os.path.exists(COUNTER_FILE):
			with open(COUNTER_FILE, 'r') as counter_file:
				lines = counter_file.readlines()
				found = False
				for line in lines:
					date, count = line.strip().split(' ')
					if date == current_date:
						updated_lines.append(f"{current_date} {counter}\n")
						found = True
					else:
						updated_lines.append(line)
				if not found:
					updated_lines.append(f"{current_date} {counter}\n")
		else:
			updated_lines.append(f"{current_date} {counter}\n")

		with open(COUNTER_FILE, 'w') as counter_file:
			counter_file.writelines(updated_lines)

		return send_from_directory(STATIC_FOLDER, 'pixel.png')
	except Exception as e:
		app.logger.error(f"Error logging visit: {e}")
		return jsonify({"error":"Internal Server Error"}), 500


@app.route('/dashboard')
@requires_auth
def dashboard():
	try:
		data = {}
		if os.path.exists(COUNTER_FILE):
			with open(COUNTER_FILE, 'r') as counter_file:
				for line in counter_file:
					date, count = line.strip().split(' ')
					data[date] = int(count)
		return jsonify(data)
	except Exception as e:
		app.logger.error(f"Error retrieving dashboard data: {e}")
		return jsonify({"error":"Internal Server Error"}), 500


@app.errorhandler(404)
def page_not_found(e):
	return jsonify({"error":"Page not found"}), 404


@app.errorhandler(500)
def internal_server_error(e):
	return jsonify({"error":"Internal Server Error"}), 500


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5003, debug=True)
