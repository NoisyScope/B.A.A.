# Personal Automation Hub Template

## 1. Overview

This project serves as a template for creating personal web automation tasks. It provides a containerized environment using Docker and Docker Compose, featuring:

*   A **Flask web application** (`web` service) as the front-end, allowing users to trigger automation tasks via a Bootstrap-styled UI.
*   A **Selenium Runner** (`selenium-runner` service) acting as a backend API (also built with Flask). This service receives commands from the web app and executes browser automation scripts using Selenium.
*   A **Selenium Standalone Chrome** (`selenium` service) providing the browser environment controlled by the Selenium Runner.
*   Comprehensive **logging** for debugging and monitoring, with logs persisted to the host machine.

The primary goal is to offer a clean, debuggable, and extensible foundation for building various browser-based automation functions.

## 2. Features

*   **Dockerized Environment**: Easy setup and consistent execution across different machines.
*   **Separation of Concerns**:
    *   UI (Flask `web` app)
    *   Automation Logic (Flask `selenium-runner` API)
    *   Browser (Selenium standalone Chrome)
*   **Web Interface**: User-friendly UI built with Bootstrap to trigger actions.
*   **API-driven Selenium**: The `selenium-runner` exposes an API for Selenium tasks, allowing for flexible integration.
*   **Persistent Logging**: Logs from both the web app and the Selenium runner are saved to a `./logs` directory on the host.
*   **Health Checks**: Services in `docker-compose.yml` include health checks for better reliability.
*   **Extensible**: Designed to be easily extended with new automation scripts and UI features.

## 3. Project Structure

```
.
├── app/                    # Main Flask web application (UI)
│   ├── main.py             # Flask app logic and routes
│   ├── templates/          # HTML templates (e.g., index.html)
│   ├── static/             # Static files (CSS, JS - if not using CDN)
│   ├── Dockerfile          # Dockerfile for the web app
│   └── requirements.txt    # Python dependencies for the web app
├── selenium_driver/        # Contains the Selenium automation script (runs as selenium-runner)
│   ├── driver.py           # Selenium script, now a Flask API service
│   └── requirements.txt    # Python dependencies for driver.py (Selenium, Flask)
├── selenium_runner/        # Dockerfile for the selenium-runner service
│   └── Dockerfile          # Builds the selenium-runner image using files from selenium_driver/
├── logs/                   # Log files will be created here (gitignored by default)
│   ├── flask_app.log       # Logs from the main web application
│   └── selenium_driver.log # Logs from the Selenium runner service
│   └── *.png               # Screenshots taken by Selenium
│   └── *.html              # Page sources saved on error by Selenium
├── docker-compose.yml      # Docker Compose configuration file
└── README.md               # This file
```

## 4. Prerequisites

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## 5. Setup and Running the Project

1.  **Clone the repository** (if applicable) or ensure you have all the project files.

2.  **Build the Docker images**:
    Open a terminal in the project root directory and run:
    ```bash
    docker-compose build
    ```

3.  **Start the application**:
    ```bash
    docker-compose up
    ```
    To run in detached mode (in the background), use:
    ```bash
    docker-compose up -d
    ```
    You should see logs from all three services starting up. Wait for the health checks to pass, especially for `selenium-runner`.

4.  **Stop the application**:
    To stop the services, press `Ctrl+C` in the terminal where `docker-compose up` is running. If running in detached mode, or from another terminal, use:
    ```bash
    docker-compose down
    ```
    This will stop and remove the containers. Add `-v` if you want to remove volumes (though this project primarily uses bind mounts for logs and code).

## 6. Usage

### Accessing the Web Application
Once the services are running, open your web browser and navigate to:
[http://localhost:5000](http://localhost:5000)

You should see the "Automation Hub" control panel.

### Triggering Selenium Actions
1.  Enter a URL you want the Selenium driver to navigate to (e.g., `https://www.google.com`).
2.  Select an action from the dropdown (currently "Navigate & Screenshot" is the main implemented action).
3.  Click the "Execute Action" button.

The Flask web app (`web` service) will send a request to the `selenium-runner` service API (at `http://selenium-runner:5001/run_selenium`). The `selenium-runner` will then use the `selenium` service to open a Chrome browser, perform the action, and save a screenshot (and logs) to the `./logs` directory.
Status messages will be displayed on the web page.

## 7. Logging and Debugging

*   **Flask Web App Logs**: Found in `./logs/flask_app.log`. These logs detail requests to the web UI and its communication attempts with the `selenium-runner`.
*   **Selenium Runner Logs**: Found in `./logs/selenium_driver.log`. These logs detail received API requests, Selenium WebDriver initialization, browser actions, errors during automation, and paths to saved screenshots/page sources.
*   **Screenshots**: Saved in `./logs/` with filenames like `screenshot_<sanitized_url>_<timestamp>.png`.
*   **Page Sources on Error**: If Selenium encounters a WebDriver error during an action, it may save the page source to `./logs/pagesource_<sanitized_url>_<timestamp>_error.html`.

You can also view live logs from all services by running `docker-compose logs -f` or for a specific service, e.g., `docker-compose logs -f selenium-runner`.

## 8. Customization and Development

This project is a template. Here are some ways to extend it:

*   **Adding New Selenium Actions**:
    1.  Modify `selenium_driver/driver.py`:
        *   Add a new case to the `perform_selenium_action` function for your new action.
        *   Implement the Selenium logic for this action.
    2.  Modify `app/templates/index.html`:
        *   Add a new option to the `<select>` dropdown for your action.
*   **Modifying the Flask Web App**:
    *   Edit `app/main.py` for backend logic.
    *   Edit `app/templates/index.html` for UI changes.
    *   Thanks to the volume mount (`./app:/app`) in `docker-compose.yml`, changes to the `web` app's Python files should auto-reload if Flask's debug mode is enabled (currently it's not in `CMD ["python", "main.py"]` for production-like behavior, but `python -m flask run --debug --host=0.0.0.0` would enable it). For template changes, a browser refresh is usually sufficient.
*   **Modifying the Selenium Runner**:
    *   Changes to `selenium_driver/driver.py` (the Flask API for Selenium) will also auto-reload due to Flask's reloader and the volume mount if you run `flask run --debug`. The current `CMD ["flask", "run"]` in `selenium_runner/Dockerfile` does not enable debug mode by default, but you can modify the CMD or temporarily shell into the container to run it with debug. Rebuilding the `selenium-runner` image (`docker-compose build selenium-runner`) and restarting (`docker-compose up -d --no-deps selenium-runner`) is the standard way to apply changes if not using live reload.

## 9. Troubleshooting

*   **Port Conflicts**: If ports `5000`, `5001`, or `4444` are already in use on your host, `docker-compose up` will fail. Change the host-side port mapping in `docker-compose.yml` (e.g., `"8080:5000"` instead of `"5000:5000"`).
*   **`selenium-runner` fails to start or is unhealthy**:
    *   Check its logs: `docker-compose logs selenium-runner`.
    *   Ensure the `selenium` service is healthy: `docker-compose logs selenium`. It needs to be up before `selenium-runner` can connect to it.
    *   The `start_period` for the healthcheck in `docker-compose.yml` gives it time, but complex initializations might take longer.
*   **Permissions issues with `./logs` directory**: If logs or screenshots aren't appearing, ensure the `./logs` directory has been created on your host and that Docker has permission to write to it. The Dockerfiles attempt to manage permissions within the container, but host mount permissions can sometimes be tricky depending on your OS and Docker setup.

---
This README provides a starting point. Feel free to expand it as you develop your specific automation tasks!
