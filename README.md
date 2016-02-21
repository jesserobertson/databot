# databot

CKAN integration for slack

### What does it do?

Searches an arbitrary CKAN instance from slack for data. You just ask `databot find <x>` and databot does the rest.

![Databot scrot](https://raw.githubusercontent.com/jesserobertson/databot/master/databotscrot.png "Databot scrot")

You can specify any CKAN endpoint with v3 of the CKAN API using on, so `databot search cycling on data.gov.uk` will search the data.gov.uk CKAN instance for cycling. Our default is `data.gov.au` because Australia needs to be first in *something* after [our terrible Ashes performance this year](http://www.abc.net.au/news/2015-08-07/michael-clarke-rues-one-of-his-toughest-days/6679346?section=sport).

A search omit function has been added. Use - to not show results without a certain word. 

For example ```databot find cycling -ballarat``` will return the results, not including those that contain ```ballarat```.

### How do I run it?

To run, you'll need Python 2, and pip

Just clone the repo, drop into the base folder and install the Python dependencies with `pip install -r requirements.txt`.

Then you should be good to go - you can run the Flask dev server with

`python manage.py runserver` 

or use gunicorn to serve to the world:

`./gunicorn.sh`

Tell slack to push requests to databot to your IP address on port 5050 using the Outgoing Webhooks integration (see picture below)

![Slack Outgoing Webhooks Integration Page](https://raw.githubusercontent.com/jesserobertson/databot/master/slack-webhook.png "Slack Outgoing Webhooks Integration Page")

### Contact & contributing

You can get in touch with me on twitter [@jesserobertson](https://twitter.com/jesserobertson). 

Databot could be a bit cleverer about how it picks datasets to return - the goodness all happens inside `app/bot.py` so feel free to have a play around and improve it. 

I find that installing httpie is a good way to play with databot on your local machine - just do `pip install httpie`, then start up the dev server in the databot root directory with `python manage.py runserver`, and then you can do something like:

```
jess@host $ http post :5000 user_name=jess text="databot find cycling"
 
HTTP/1.0 200 OK
Content-Length: 464
Content-Type: application/json
Date: Fri, 07 Aug 2015 02:36:33 GMT
Server: Werkzeug/0.10.4 Python/2.7.10

{
    "text": "Thanks @jess. I found 50 results for cycling at data.gov.au, here's the top result:\nSouth Australian residents riding a bicycle in a typical week (it's a XLS file). Get it <https://data.sa.gov.au/data/dataset/a79f87b6-9710-4fa6-8be3-8b2f8c29ac45/resource/0fe26a5a-ca1e-4fd3-aa2c-56f8ef386272/download/2cycling2014pr.xlsx|here>.\nWant more? Check out <http://data.gov.au/dataset?q=cycling&sort=extras_harvest_portal+asc%2C+score+desc|this link>."
}
```

Enjoy!
