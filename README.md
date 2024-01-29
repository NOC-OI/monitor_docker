# Docker Container Monitor for Virtual Machines

This repository provides a solution for monitoring the operation of Docker containers on a virtual machine (VM). The monitoring package functions as follows:

- At defined time intervals, a script on the VM saves a CSV file containing the status of all containers, including those that have already completed their execution.

- A set of commands within a Docker container, also on the VM, evaluates this CSV file. If there are any changes in the status of the containers or if they are not functioning properly, an email group is notified.

- In case any container encounters an issue, an email is sent with the subject "Issues with container(s): {container-names}."

- When the situation returns to normal, an email with the subject "Containers OK!" is sent, indicating that all containers are functioning correctly.

## Prerequisites

Before using this package, you need to set the following environment variables:

- `EMAIL_FROM`: The email address from which the messages will be sent.
- `EMAIL_PWD`: A sixteen-character password for accessing the email. Note that this password is different from your email account password.

Save these variables in a `.env` file at the root of the repository, following this example:

```env
EMAIL_FROM='imfepilotdockermonitoring@gmail.com'
EMAIL_PWD='aaaa aaaa aaaa aaaa'
```

## Configure the Email

This project uses a Gmail account to send alert emails. To set up the Gmail account, follow these steps:

1. Create a new Gmail account, for example, `imfepilotdockermonitoring@gmail.com`.
2. Access your account settings using this link: [Google Account Settings](https://myaccount.google.com).
3. Click on "Security" and scroll down to the section "Signing in to Google." Click on "2-Step Verification" to activate it.
4. Follow the prompts to add a phone number and enable "2-Step Verification."
5. Generate a password for your app by going to the link [App Passwords](https://myaccount.google.com/apppasswords). You may need to enter your Gmail account credentials again.
6. Select the app type as "Other (Custom Name)" and provide a name that identifies your app.
7. Click on `GENERATE`, and you will receive a sixteen-character password. Use this password for the `EMAIL_PWD` environment variable.

## Commands to Execute on the VM

To make this container function, you must configure the VM with a cron task to execute and save container status files in a specific VM folder. Add the following command to the cron tab on the VM:

```bash
*/5 * * * * {ssh-command-path}/docker_status_checker.sh >> {ssh-command-path}/data/cron.log 2>&1
```

In the example above, the "docker_status_checker.sh" script is executed every 5 minutes. Be sure to generate and save the log file of the code results in the specified folder, referred to as "ssh-command-path."

The "docker_status_checker" code will save a file with the status of all running containers in a file named "containers_status.csv," which should be saved in the "'ssh-command-path'/data" folder. You may need to create the "data" folder in the directory and ensure that the `docker_status_checker.sh` file matches the paths of the `ssh-command-path`.

## Containers' Status to Be Checked

The "information.json" file contains the expected status of the containers to be monitored, as well as the list of email addresses to be notified when there are updates regarding their operation. The format of the "information.json" file should be as follows:

```json
{
  "containers": [
    {"name": {container-name1}, "image": {image-name1}, "port": {port-number1}},
    {"name": {container-name2}, "image": {image-name2}, "port": {port-number2}}
  ],
  "email_to": [{email1}, {email2}]
}
```

Here is an example of a pre-filled "information.json" file:

```json
{
  "containers": [
    {"name": "api_calculations_use_cases", "image": "docker-repo.bodc.me/oceaninfo/imfe-pilot/api_calculations_use_cases_web:latest", "port": "8081"},
    {"name": "tile-server", "image": "docker-repo.bodc.me/oceaninfo/imfe-pilot/titiler-uvicorn:latest", "port": "8083"},
    {"name": "mbtiles", "image": "docker-repo.bodc.me/oceaninfo/imfe-pilot/mbtiles:latest", "port": "8082"},
    {"name": "frontend", "image": "docker-repo.bodc.me/oceaninfo/imfe-pilot/frontend:latest", "port": "8080"}
  ],
  "email_to": ["tobias.ferreira@noc.ac.uk", "tobias.ramalho.ferreira@gmail.com"]
}
```

## Package Execution

To run all package commands as a single script, use the "scripts/monitor_docker-run" file.

## Controlling Jobs Within the Container (Cron Tab)

The "container_cronjob" file represents the cron tab file that will be executed within the container. This cron command will execute the "scripts/monitor_docker-run" code at the frequency defined in the "container_cronjob" file.

## CI/CD (Continuous Integration/Continuous Deployment)

The ".gitlab-ci.yml" file presents the CI/CD setup for this package. In this file, pay attention to the lines in the "deploy" stage:

```yaml
- ssh web "mkdir -p {ssh-command-path} && cp .monitor_docker-env {ssh-command-path}/.env"
- scp -r data web:{ssh-command-path}
- ssh web 'docker run --env-file {ssh-command-path}/.env -v {ssh-command-path}/data/:/data -d -t --name monitor_docker docker-repo.bodc.me/oceaninfo/imfe-pilot/monitor_docker:latest'
- ssh web 'docker cp {ssh-command-path}/data/containers_status.csv monitor_docker:/data/'
```

Ensure that the value of "ssh-command-path" matches the previously defined path. In this code, a volume is created on the VM in the path "'ssh-command-path'/data/" representing the "/data/" folder within the container. Note that you may also need to specify the tag of your Docker image if you are using a different container registry.

Additionally, create a file called `.monitor_docker-env` in your GitLab Runner home folder and include the necessary environment variables for this project.

## Testing the Code Locally

To test the code locally, follow these steps:

1. Install the package by running:

```bash
pip install -e .
```

2. Generate the "containers_status.csv" file by executing the following command:

```bash
docker_status_checker_local.sh
```

3. Create an "information.json" file with the information about the containers you want to monitor and the email addresses.

4. Run the "monitor_docker-run" command as follows:

```bash
monitor_docker-run
```

If there are any issues with the containers that differ from the expected status, an email will be sent to the recipients specified in the "information.json" file.
