from flask import Flask, send_from_directory, request
import os
from datetime import datetime

app = Flask(__name__)

STATIC_FOLDER = 'static'
LOG_FOLDER = 'logs'
LOG_FILE = os.path.join(LOG_FOLDER, 'visits.log')

os.makedirs(LOG_FOLDER, exist_ok=True)

@app.route('/pixel.png')
def tracking_pixel():
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.now()}, {request.remote_addr}, {request.headers.get('User-Agent')}\n")
    return send_from_directory(STATIC_FOLDER, 'pixel.png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
