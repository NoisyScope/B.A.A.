FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP driver.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5001
# Optional: Default sleep time for page loads in driver.py
ENV SELENIUM_PAGE_LOAD_SLEEP 5

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY selenium_driver/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the driver script that now contains the Flask app
COPY selenium_driver/driver.py /app/driver.py

# Create logs directory and set permissions.
# The script also tries os.makedirs(LOG_DIR, exist_ok=True)
# This is more explicit for Docker build stage.
RUN mkdir -p /app/logs && \
    chown -R nobody:nogroup /app/logs && \
    chmod -R 777 /app/logs && \
    chown -R nobody:nogroup /app && \
    chmod -R 777 /app # Make app dir writable for user nobody if needed for some reason


# Switch to a non-root user for security (optional, but good practice)
# USER nobody

EXPOSE 5001

# CMD ["python", "driver.py"]
# Using Flask's CLI runner can be more robust for some configurations
CMD ["flask", "run"]
