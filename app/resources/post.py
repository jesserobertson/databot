import random
import json
import requests

from flask import current_app, url_for, abort
from flask.ext.restful import Resource, reqparse, fields, marshal, inputs, marshal_with

post_fields = {
    'token': fields.String,
    'team_id': fields.String,
    'team_domain': fields.String,
    'channel_id': fields.String,
    'channel_name': fields.String,
    'timestamp': fields.String,
    'user_id': fields.String,
    'user_name': fields.String,
    'text': fields.String,
    'trigger_word': fields.String
}

class Bot(object):
    
    """ An individual Bot conversation
    """
    
    default_endpoint = 'data.gov.au'
    
    def __init__(self, **kwargs):
        # Copy in all data
        super(Bot, self).__init__()
        for arg, value in kwargs.items():
            setattr(self, arg, value)
    
    def respond(self, text=None, **kwargs):
        """ Send a response back to the app
        """
        if text is None:
            text = 'Hello {0.user_name}, how can I help?'
        content = {
            'token': 'xoxb-8725697458-96LgtIBgQldEvWG8KF0ihv2b',
            'text': text.format(self),
            'channel': self.channel_id
        }
        if kwargs:
            content.update(kwargs)
        print ' -- ' + content['text']
#         requests.post('https://slack.com/api/chat.postMessage', data=content)

    def chat(self):
        """ Parse the text requests and post responses
        """
        # Strip text of @databot[:]
        try:
            tokens = self.text.split()[1:]
            first = tokens.pop(0)
        except IndexError:
            return self.respond('Hello @{0.user_name}, how can I help?')
            
        # First token should be 'find', if not, just say hello
        if first != 'find':
            return self.respond(
                "Sorry @{0.user_name}, I didn't understand that")

        # if second last token is 'on', then we want to search on 
        # a particular portal
        try:
            if tokens[-2] == 'on':
                # Pop off last two tokens cause we don't care about these
                self.endpoint = tokens.pop()
                _ = tokens.pop()
            else:
                # Use data.gov.au as default endpoint
                self.endpoint = self.default_endpoint
        except IndexError:
            self.endpoint = self.default_endpoint

        # Make sure we can query the endpoint
        self.short_endpoint = self.endpoint
        if not self.endpoint.startswith('http'):
            self.endpoint = 'http://' + self.endpoint
        self.endpoint = self.endpoint + '/api/3/action'

        # If second token is 'anything', we do a random search
        if tokens[0] == 'anything':
            return self.random()

        # If second token is 'changed', we do a changed search
        elif tokens[0] == 'changes':
            return self.changed()

        # Glom everything else into a query
        return self.query(tokens)

    def first_response(self):
        """ Post an acknowledgement that you've got something
        """
        response = [
            "I'm just looking that up in the Pokedex.",
            "I'll just have to whip the interns some more...",
            "Are you sure that's a good idea?",
            "Would your grandmother be happy reading that?",
            "I'm just logging your query with ASIO."
        ]
        self.respond("Thanks @{{0.user_name}}. {0}".format(random.choice(response)))

    
    def query(self, tokens):
        """ Run a query
        """
        self.first_response()
        
        # Run the query
        query = '+'.join(tokens)
        data = {'q': query, 'rows': 10}
        response = requests.get(self.endpoint + '/package_search', data=query)
        
        # Respond with a few answers
        if response.ok:
            results = response.json()
            count = results['result']['count']
            self.respond(("I found {0} results "
                         "for {1} at {{0.short_endpoint}}, "
                         "here's the top ten:").format(count, query))
            for result in results['result']['results']:
                template = "{1} (it's a {0} file). Get it here: {2}"
                description = result['resources'][0]['description'].split('.')[0]
                link = result['resources'][0]['url']
                fmt = result['resources'][0]['format']
                self.respond(template.format(fmt, description, link))
        else:
            self.respond("Looks like something's borked at "
                         "{0.short_endpoint}, you're on your own!")
    
    def random(self):
        """ Return a random dataset
        """
#         self.first_response()
        self.respond("I can't let you do that @{0.user_name}.")

    def changed(self):
        """ Return the datasets which have changed recently
        """
        response = requests.get(
            self.endpoint + '/recently_changed_packages_activity_list')
        
        # Respond with a few answers
        if response.ok:
            results = response.json()
            count = results['result']['count']
            self.respond(("I found {0} results "
                         "which have recently changed at {{0.short_endpoint}}, "
                         "here's the top ten:").format(count, query))
            for result in results['result']['results']:
                template = "{1} (it's a {0} file). Get it here: {2}"
                description = result['resources'][0]['description'].split('.')[0]
                link = result['resources'][0]['url']
                fmt = result['resources'][0]['format']
                self.respond(template.format(fmt, description, link))
        else:
            self.respond("Looks like something's borked at "
                         "{0.short_endpoint}, you're on your own!")



class PostAPI(Resource):

    slack_data = ('token', 'team_id', 'team_domain', 'channel_id',
                  'channel_name', 'timestamp', 'user_id', 'user_name',
                  'text', 'trigger_word')

    def __init__(self):
        # Validate input
        self.reqparse = reqparse.RequestParser()
        for arg in post_fields.keys():
            self.reqparse.add_argument(arg, type=str, default=None)

        # Initialize the resource
        super(PostAPI, self).__init__()

    def get(self):
        return {'message': 'Databot says "Hello, World!"'}

    def post(self):
        post = Bot(**self.reqparse.parse_args()).chat()