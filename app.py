from flask import Flask, send_from_directory, request, jsonify, Response
import os
from datetime import datetime
import logging
import sqlite3
from functools import wraps

app = Flask(__name__)

STATIC_FOLDER = 'static'
LOG_FOLDER = 'logs'
DATABASE = 'visits.db'

os.makedirs(LOG_FOLDER, exist_ok=True)

# Инициализация логирования
logging.basicConfig(filename='app.log', level=logging.DEBUG)

def check_auth(username, password):
    return username == 'lime_checker' and password == 'ldw12fggAgfgh3gG[[vRF'


# Запрос логина и пароля
def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


# Декоратор для защиты маршрута
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def log_visit(ip, user_agent):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO visits (timestamp, ip, user_agent) VALUES (?, ?, ?)',
                   (datetime.now(), ip, user_agent))
    conn.commit()
    conn.close()


def update_counter():
    current_date = datetime.now().strftime('%d-%m-%Y')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT count FROM counter WHERE date = ?', (current_date,))
    row = cursor.fetchone()
    if row:
        counter = row[0] + 1
        cursor.execute('UPDATE counter SET count = ? WHERE date = ?', (counter, current_date))
    else:
        counter = 1
        cursor.execute('INSERT INTO counter (date, count) VALUES (?, ?)', (current_date, counter))
    conn.commit()
    conn.close()
    return counter


@app.route('/pixel.png')
def tracking_pixel():
    try:
        log_visit(request.remote_addr, request.headers.get('User-Agent'))
        counter = update_counter()
        logging.debug(f"Current counter value: {counter}")
        return send_from_directory(STATIC_FOLDER, 'pixel.png')
    except Exception as e:
        app.logger.error(f"Error logging visit: {e}")
        logging.error(f"Exception occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/dashboard')
@requires_auth
def dashboard():
    try:
        data = {}
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM counter')
        rows = cursor.fetchall()
        for row in rows:
            data[row[0]] = row[1]
        conn.close()
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error retrieving dashboard data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
