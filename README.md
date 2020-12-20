# PUBLISH REDDIT SUBREDDITS AS TOPICS IN KAFKA

## START PRODUCER

You need first to register as a bot in reddit, getting a client id, a client secret.
Create an .env file from .env.template and fill in the the missing information.
Host will be `kafka` while starting `docker-compose up`.
Start as `docker-compose up`

## START CONSUMER

For this, the assumption that you can create a python environment with the libraries defined in `requirements.txt`, add a line to `/etc/hosts` having `127.0.0.1 kafka localhost`, set the environment variable `host` to `kafka` and then execute the python script `consume.py`.