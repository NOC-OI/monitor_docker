FROM python:3.9

COPY . .
COPY ./.env.copy .env

COPY ./information.json information.json

RUN pip install --upgrade pip
RUN pip install -e .
RUN apt-get -y update 
RUN apt-get install cron -y && apt-get install vim -y

# Crontab file copied to cron.d directory.
COPY ./container_cronjob /etc/cron.d/container_cronjob

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/container_cronjob

# Apply cron job
RUN crontab /etc/cron.d/container_cronjob

# Create the log file to be able to run tail
RUN touch /data/cron.log

# Run the command on container startup
CMD cron && tail -f /data/cron.log
