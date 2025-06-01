# Use a Selenium standalone Chrome image
FROM selenium/standalone-chrome:latest

# The image already has Selenium Grid and WebDriver installed and configured.
# It exposes port 4444 by default.

# We might need to copy our driver script into this container if we decide
# to run it from here, but for now, the docker-compose setup will have a separate service for the script.
# For now, this Dockerfile is minimal as the base image does most of the work.

# Add a health check
HEALTHCHECK CMD curl --fail http://localhost:4444/wd/hub/status || exit 1

USER seluser
ENV HOME /home/seluser
ENV PATH $HOME/.local/bin:$PATH

# If we needed to install python and run driver.py from this container:
# USER root
# RUN apt-get update && apt-get install -y python3 python3-pip
# RUN pip3 install selenium
# COPY driver.py /app/driver.py
# COPY requirements.txt /app/requirements.txt
# RUN pip3 install -r /app/requirements.txt
# WORKDIR /app
# CMD ["python3", "driver.py"]
# However, we will use a separate service for the python script runner.
# So this Dockerfile remains very simple.
# The base image's default entrypoint will start the Selenium server.
# Expose the port for Selenium Grid/Server
EXPOSE 4444
