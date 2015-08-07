# databot

CKAN integration for slack

### What does it do?

Searches an arbitrary CKAN instance from slack for data. You just ask `databot find <x>` and databot does the rest.

![Databot scrot](https://raw.githubusercontent.com/jesserobertson/databot/master/databotscrot.png "Databot scrot")

You can specify any CKAN endpoint with v3 of the CKAN API using on, so `databot search cycling on data.gov.uk` will search the data.gov.uk CKAN instance for cycling. Our default is `data.gov.au` because Australia needs to be first in *something* after [our terrible Ashes performance this year](http://www.abc.net.au/news/2015-08-07/michael-clarke-rues-one-of-his-toughest-days/6679346?section=sport).

### How do I run it?

To run, you'll need Python 2, and pip

Just clone the repo, drop into the base folder and install the Python dependencies with `pip install -r requirements.txt`.

Then you should be good to go - you can run the Flask dev server with

`python manage.py runserver` 

or use gunicorn to serve to the world:

`./gunicorn.sh`

Tell slack to push requests to databot to your IP address on port 5050 using the Outgoing Webhooks integration (see picture below)

![Slack Outgoing Webhooks Integration Page](https://raw.githubusercontent.com/jesserobertson/databot/master/slack-webhook.png "Slack Outgoing Webhooks Integration Page")
