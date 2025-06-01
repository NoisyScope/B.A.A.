import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
import logging
from flask import Flask, request, jsonify
import datetime

# --- Logger Setup ---
LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, "selenium_driver.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
app = Flask(__name__)

SELENIUM_HUB_URL = 'http://selenium:4444/wd/hub'
MAX_RETRIES_DRIVER_SETUP = 3 # Reduced for faster failure if config is wrong
RETRY_DELAY_DRIVER_SETUP = 5

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--remote-debugging-port=9222")


    for attempt in range(1, MAX_RETRIES_DRIVER_SETUP + 1):
        try:
            logging.info(f"Connecting to Selenium Hub: {SELENIUM_HUB_URL} (Attempt {attempt}/{MAX_RETRIES_DRIVER_SETUP})")
            driver = webdriver.Remote(command_executor=SELENIUM_HUB_URL, options=chrome_options)
            driver.set_page_load_timeout(40)
            driver.set_script_timeout(30)
            logging.info("WebDriver initialized successfully.")
            return driver
        except (WebDriverException, ConnectionRefusedError) as e:
            logging.error(f"WebDriver setup attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES_DRIVER_SETUP:
                logging.error("Max retries reached for WebDriver setup.")
                raise
            time.sleep(RETRY_DELAY_DRIVER_SETUP)
    return None # Should not be reached

def perform_selenium_action(driver, action, url):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_url_part = url.split('//')[-1].replace('/', '_').replace(':', '_').replace('.', '_')[:50]

    try:
        logging.info(f"Navigating to URL: {url}")
        driver.get(url)
        # Consider WebDriverWait here instead of time.sleep for robustness
        time.sleep(max(5, int(os.environ.get("SELENIUM_PAGE_LOAD_SLEEP", "5"))))


        if action == "navigate_and_screenshot":
            screenshot_filename = f"screenshot_{sanitized_url_part}_{timestamp}.png"
            screenshot_path = os.path.join(LOG_DIR, screenshot_filename)
            logging.info(f"Taking screenshot of {url}")
            driver.save_screenshot(screenshot_path)
            logging.info(f"Screenshot saved to {screenshot_path}")
            return {"status": "success", "message": f"Navigated to {url} and saved screenshot.", "screenshot_path": screenshot_path}
        else:
            logging.warning(f"Unknown action: {action}")
            return {"status": "warning", "message": f"Unknown action: {action}"}
    except TimeoutException as te:
        logging.error(f"Timeout on {url} for action '{action}': {te}")
        return {"status": "error", "message": f"Timeout: {te}"}
    except WebDriverException as wde:
        logging.error(f"WebDriverException on {url} for '{action}': {wde}")
        # Attempt to save page source for debugging
        page_source_filename = f"pagesource_{sanitized_url_part}_{timestamp}_error.html"
        page_source_path = os.path.join(LOG_DIR, page_source_filename)
        try:
            if driver and hasattr(driver, 'page_source'):
                 with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                 logging.info(f"Page source saved to {page_source_path}")
        except Exception as pse:
            logging.error(f"Failed to save page source: {pse}")
        return {"status": "error", "message": f"WebDriver error: {wde}. Page source saved if possible."}
    except Exception as e:
        logging.error(f"Unexpected error on {url} for '{action}': {e}", exc_info=True)
        return {"status": "error", "message": f"Unexpected error: {e}"}

@app.route('/run_selenium', methods=['POST'])
def run_selenium_task_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400
    url = data.get('url')
    action = data.get('action', 'navigate_and_screenshot')
    if not url:
        return jsonify({"status": "error", "message": "'url' is required"}), 400

    logging.info(f"Received task: action='{action}', url='{url}'")
    driver = None
    try:
        driver = setup_driver()
        if not driver:
             return jsonify({"status": "error", "message": "Failed to initialize WebDriver."}), 500
        result = perform_selenium_action(driver, action, url)
        return jsonify(result), 200 if result.get("status") == "success" else 500
    except Exception as e:
        logging.error(f"Error in /run_selenium: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Internal server error: {e}"}), 500
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"Error quitting WebDriver: {e}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check_endpoint():
    logging.info("Health check requested.")
    # Could add a quick check to Selenium hub if desired
    return jsonify({"status": "healthy", "message": "Selenium Runner is up."})

if __name__ == '__main__':
    if not os.access(LOG_DIR, os.W_OK):
        logging.warning(f"Log directory {LOG_DIR} may not be writable by UID {os.getuid()}.")
    logging.info(f"Starting Selenium Runner Flask app on port 5001. Logging to {log_file_path}")
    app.run(host='0.0.0.0', port=5001, debug=False)
