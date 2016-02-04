""" file:   bot.py (databot.app)
    
    description: Bot class to make a chatty databot


"""

from utilities import filter_results_by_term

import requests
from time import sleep
import json

MAX_CHAR_LIMIT = 160

consumer_key = "cjUlJQr8ukJpwSMnq5w1EQkbE"
consumer_secret = "dckLfSNywCSIecVGjW8rbLMUlLAfKjzDFwUQTrduLOiTKiGGFZ"
access_token = "4718417858-D0UbpDi30tN0ahxPPX0EZZuBStTp2HtKGdPN5AK"
access_token_secret = "bCvERaLZCWgLy8AmEAP6in6b1v6bLhFrYSFyMGZcA9wu0"

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import pdb
# This is a basic listener that just prints received tweets to stdout.


class StdOutListener(StreamListener):
    def on_data(self, data):
        print data
        print data
        bot = Bot(data['text'])
        response = {
            'status': bot.response[:MAX_CHAR_LIMIT],
            'in_reply_to_status_id': data['id']
        }
        header = dict(Authorization='OAuth',
                      oauth_consumer_key="cjUlJQr8ukJpwSMnq5w1EQkbE",
                      oauth_nonce="10a7126927cd44cacacad6ef216d27e5",
                      oauth_signature="6v6j1zOLdSnHrH1pSY0N7FOEGx0%3D",
                      oauth_signature_method="HMAC-SHA1",
                      oauth_timestamp="1454588110",
                      oauth_token="4718417858-D0UbpDi30tN0ahxPPX0EZZuBStTp2HtKGdPN5AK",
                      oauth_version="1.0")

        requests.post(
            "https://api.twitter.com/1.1/statuses/", headers=header, json=response)
        return True

    def on_error(self, status):
        print status


class Bot(object):

    """ An individual Bot conversation
    """

    default_endpoint = 'data.gov.au'

    def __init__(self, **kwargs):
        # Copy in all data
        super(Bot, self).__init__()
        for arg, value in kwargs.items():
            setattr(self, arg, value)

        # Set up response
        self.response = {
            'status': '',
            'in_reply_to_status_id': ''
        }

        # Run chat
        # We need to replace links in slack with the default values, if given
        # since slack does data.gov.au -> <http://data.gov.au|data.gov.au>
        # so we regexp it and replace

        # Strip text of first token which is always 'databot'
        try:
            tokens = self.text.split()[1:]
            first = tokens.pop(0)
        except IndexError:
            return self.respond('Hello @{0.user_name}, how can I help?')

        # First token should be 'find', if not, just say hello
        if first != 'find':
            return self.respond(
                "Sorry @{0.user_name}, I didn't understand that")
        else:
            self.respond('Thanks @{[user][name]}. ')

        # if second last token is 'on', then we want to search on
        # a particular portal
        try:
            if tokens[-2] == 'on':
                # Pop off last two tokens cause we don't care about these
                self.endpoint = tokens[-1]
                tokens = tokens[:-2]
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

    def respond(self, text):
        """ Send a response back to the app
        """
        self.response['text'] += text.format(self)

    def send_file_info(self, result):
        """ Print info about a single file result from the api
        """
        try:
            # Get info from result
            description = result['resources'][0]['description'].split('.')[0]
            if description in ('', None):
                description = "There's no description for this file"
            link = result['resources'][0]['url']
            fmt = result['resources'][0]['format']
            if fmt in ('', None):
                fmt = 'in an unknown format'
            else:
                if any(fmt.startswith(v) for v in 'aeiou'):
                    fmt = 'an ' + fmt + ' file'
                else:
                    fmt = 'a ' + fmt + ' file'

            # Post message
            template = u"{1} (it's {0}). Get it <{2}|here>."
            self.respond(template.format(fmt, description, link))
        except IndexError:
            self.respond(
                "Hmm, I've found a resource here but can't parse it. Moving on...")

    def query(self, tokens):
        """ Run a query
        """
        # Jas@20/1/16 - If a token has a - in front, it is removed and placed
        # in filter_out
        filter_out = {t.lstrip('-') for t in tokens if t.startswith('-')}
        tokens = {t for t in tokens if not t.startswith('-')}

        # Run the query
        query = '+'.join(tokens)

        # Jas@20/1/16 - I made rows : 100, to give the user more details abot what's being
        # filtered with search terms.
        data = {'q': query, 'rows': 100}
        query_response = requests.get(
            self.endpoint + '/package_search', params=data)

        # Jas@20/1/16 - Some changes to this condition statement, to reflect filtered results
        # Respond with a few answers
        if query_response.ok:
            results = query_response.json()
            count = results['result']['count']
            results = results['result']['results']

            # Remove filtered terms
            if len(filter_out) > 0:
                results, filtered_count = \
                    filter_results_by_term(results, filter_out)
            else:
                filtered_count = 0

            # Generate response
            if count > 0:
                self.respond(("I found {0} results "
                              "for {1} at {{0.short_endpoint}}. ").format(count, query))
                if filtered_count > 0:
                    self.respond(("From the top 100 results, I removed {0} with these"
                                  " terms: {1}. ").format(filtered_count, ', '.join(filter_out)))
                    self.respond(
                        "Here's the top result from the filtered list:\n")
                else:
                    self.respond("Here's the top result:\n")
                if len(results) > 0:
                    self.send_file_info(results[0])
                else:
                    self.respond("nil")
                more_link = (
                    "http://{{0.short_endpoint}}/dataset?q={0}"
                    "&sort=extras_harvest_portal+asc%2C+score+desc").format(query)
                self.respond(
                    ("\nWant more? Check out <{0}|this link>.".format(more_link)))
            else:
                self.respond(("Sorry, I couldn't find anything"
                              " on '{0}' at {{0.short_endpoint}}.").format('+'.join(tokens)))
        else:
            self.respond("\nLooks like something's borked at "
                         "{0.short_endpoint}, you're on your own!")

    def random(self):
        """ Return a random dataset
        """
        self.respond("I can't let you do that @{0.user_name}.")

    def changed(self):
        """ Return the datasets which have changed recently
        """
        changed_response = requests.get(
            self.endpoint + '/recently_changed_packages_activity_list')

        # Respond with a few answers
        if changed_response.ok:
            results = changed_response.json()
            count = results['result']['count']
            self.respond(("I found {0} results which have recently changed at {{0.short_endpoint}}, "
                          "here's the top ten:").format(count))
            for result in results['result']['results']:
                self.send_file_info(result)
        else:
            self.respond("Looks like something's borked at "
                         "{0.short_endpoint}, you're on your own!")

if __name__ == '__main__':

    # This handles Twitter authetification and the connection to Twitter
    # Streaming API
    header = dict(Authorization='OAuth',
                      oauth_consumer_key="cjUlJQr8ukJpwSMnq5w1EQkbE",
                      oauth_nonce="10a7126927cd44cacacad6ef216d27e5",
                      oauth_signature="6v6j1zOLdSnHrH1pSY0N7FOEGx0%3D",
                      oauth_signature_method="HMAC-SHA1",
                      oauth_timestamp="1454588110",
                      oauth_token="4718417858-D0UbpDi30tN0ahxPPX0EZZuBStTp2HtKGdPN5AK",
                      oauth_version="1.0")
    get_url = "https://api.twitter.com/1.1/statuses/mentions_timeline.json"
    data = {'screen_name': 'databot_au',
                'since_id': None,
                'count': 1
                }

    while True:
        if data.get('since_id') is None:
            del data['since_id']
        resp = requests.get(get_url, headers=header, json=data)
        if resp.ok:
            print "woo"
        else:
            pdb.set_trace()
            sleep(10)
            continue

        sleep(10)

    # l = StdOutListener()
    # auth = OAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_token_secret)
    # stream = Stream(auth, l)
    # stream.userstream()
