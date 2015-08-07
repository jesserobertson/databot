# databot

CKAN integration for slack

### How do I run it?

To run, you'll need Python 2, and pip

Just clone the repo, drop into the base folder and install the Python dependencies with `pip install -r requirements.txt`.

Then you should be good to go - you can run the Flask dev server with

`python manage.py runserver` 

or use gunicorn to serve to the world:

`./gunicorn.sh`

Tell slack to push requests to databot to your IP address on port 5050 using the Outgoing Webhooks integration (see picture below)

![Slack Outgoing Webhooks Integration Page](https://raw.githubusercontent.com/jesserobertson/databot/master/slack-webhook.png "Slack Outgoing Webhooks Integration Page")
