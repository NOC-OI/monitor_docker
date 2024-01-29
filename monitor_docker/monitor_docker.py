"""
monitor_docker: Monitor Docker Container Package
"""
import json
import os
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class MonitorDocker:
    """MonitorDocker:
        Class for monitoring docker containers status. It sends an email
    everytime that there is a issue with some of the docker containers.
    """

    load_dotenv()

    def __init__(
        self,
        information_path: str = "/",
        status_path: str = "/data/",
    ):
        self._email_from = os.getenv("EMAIL_FROM")
        self._email_pwd = os.getenv("EMAIL_PWD")
        with open(f"{information_path}information.json", encoding="utf-8") as file_info:
            file_info = json.load(file_info)
            self.containers = file_info["containers"]
            self.email_to = file_info["email_to"]
        self.containers_status = pd.read_csv(
            f"{status_path}containers_status.csv", delimiter=",,", engine="python"
        )
        self.issues = {}

        with open(f"{status_path}cron.log", encoding="utf-8") as log_file:
            runs = log_file.read().split("\n")
            if len(runs) > 1:
                self.last_run = runs[-2]
            else:
                self.last_run = ""

    def check_containers(self, send_email=True):
        """
        check_containers: class method for checking container status.

        Args:
            send_email (bool, optional): If set to True, an email will be sent
        to a list of contacts with a description of the issues with the docker
        containers. Defaults to True.
        """
        for container in self.containers:
            issue = []
            container_df = self.containers_status[
                self.containers_status.Image == container["image"]
            ]
            if container_df.empty:
                issue.append("Container not in list.")
                self.issues[container["name"]] = issue
                continue
            status = container_df.Status.iloc[0]
            if not status.startswith("Up"):
                issue.append(f"Container not working. Current status: {status}")

            port = container_df.Ports.iloc[0]
            if str(container["port"]) not in str(port):
                issue.append(
                    f"Container not in port {container['port']}. \
                        Current port information: {port}"
                )
            if len(issue) > 0:
                self.issues[container["name"]] = issue

        if not self.containers_status.empty:
            if len(self.issues.keys()) > 0:
                subject = self.create_subject()
                content = self.create_content(subject)
                print(f"ERROR: {time.ctime()} - {subject}")
                if send_email:
                    if not self.last_run.split("-")[-1].strip() == subject:
                        self.send(subject, content)
            else:
                print(f"SUCCESS: {time.ctime()} - Everything correct")
                if self.last_run.startswith("ERROR"):
                    if send_email:
                        self.send(
                            "Containers OK!",
                            "All containers are now working correctly.",
                        )

    def create_subject(self):
        """
        create_subject: create subject for the email

        Returns:
            subject (str): email subject.
        """
        containers = self.issues.keys()
        subject = "Issues with container"
        if len(containers) > 1:
            subject += "s: "
        else:
            subject += ": "

        for container in self.issues:
            subject += f"{container}, "

        return subject[0:-2]

    def create_content(self, subject):
        """
        create_content: create email for the email

        Args:
            subject (str): Email subject.

        Returns:
            content (str): email content.
        """
        email_title = f"<h1><strong>{subject}<strong></h1>"
        email_content = ""
        for container, issues in self.issues.items():
            email_content += f"<h2>{container}</h2>"
            for issue in issues:
                email_content += f"<p>{issue}</p>"
            email_content += "<br>"

        return f"<html><head></head><body>{email_title}{email_content}</body></html>"

    def send(self, subject, content):
        """
        send: send email to the list of contacts


        Args:
            subject (str): Email subject.
            content (str): Email content.
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._email_from
        msg["To"] = (";").join(self.email_to)

        msg.attach(MIMEText(content, "html"))

        context = ssl.create_default_context()

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)

        server.login(self._email_from, self._email_pwd)
        server.sendmail(self._email_from, self.email_to, msg.as_string())
        server.quit()
