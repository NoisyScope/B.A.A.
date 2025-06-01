import logging
import os
from flask import Flask, render_template, request, jsonify

# --- Logger Setup ---
LOG_DIR = "/app/logs" # Using the mounted volume path inside the container
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file_path = os.path.join(LOG_DIR, "flask_app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler() # Also log to console
    ]
)

app = Flask(__name__)

@app.route('/')
def index():
    logging.info("Index page requested.")
    return render_template('index.html', message="Welcome to the Automation Hub!")

@app.route('/execute', methods=['POST'])
def execute_action():
    action = request.form.get('action', 'default_action')
    target_url = request.form.get('url', 'https://www.google.com') # Default URL
    logging.info(f"Received request to execute action: '{action}' on URL: '{target_url}'")

    # Placeholder for Selenium interaction
    # In a real scenario, this would involve:
    # 1. Making a request to the Selenium service (e.g., via HTTP or a message queue)
    # 2. Passing the 'action' and 'target_url'
    # 3. Receiving a response/status from the Selenium service

    # For now, simulate success
    logging.info(f"Simulating Selenium action '{action}' for URL '{target_url}'.")
    # This is where you would add code to communicate with the selenium_driver service
    # For example, using the requests library:
    # try:
    #     response = requests.post('http://selenium-runner:5001/run_selenium', json={'url': target_url, 'action': action})
    #     if response.status_code == 200:
    #         logging.info("Successfully triggered selenium task.")
    #         return jsonify({"status": "success", "message": f"Action '{action}' on '{target_url}' initiated."})
    #     else:
    #         logging.error(f"Failed to trigger selenium task. Status: {response.status_code}, Response: {response.text}")
    #         return jsonify({"status": "error", "message": "Failed to trigger selenium task."}), 500
    # except requests.exceptions.RequestException as e:
    #     logging.error(f"Error communicating with selenium-runner: {e}")
    #     return jsonify({"status": "error", "message": "Error communicating with selenium-runner."}), 500

    return jsonify({"status": "success", "message": f"Action '{action}' for URL '{target_url}' simulated successfully."})

if __name__ == '__main__':
    # Make sure the log directory is writable by the user running the app
    # In a container, this is usually root or a user with similar permissions in WORKDIR /app
    if not os.access(LOG_DIR, os.W_OK):
        logging.error(f"Log directory {LOG_DIR} is not writable.")
    else:
        logging.info(f"Flask app logs will be saved to {log_file_path}")
    app.run(host='0.0.0.0', port=5000)
