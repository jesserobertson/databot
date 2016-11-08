""" file:   twitterbot.py (databot.app)

    description: Bot class to make a chatty twitterbot
    author: Jesse Robertson
    edited by:Cameron Poole
    TODO:
        - Change keys and hide them in configfile or something
        - Sort out reply tweets.
        - Implement some kind of code counting
        - Send multiple tweets ??? one for result
        - Maybe if it user replies more ? get more ???
        - Track some of this perhaps
        - Need to implement main method and decide on deployment


"""

from utilities import filter_results_by_term

import requests
from time import sleep
# import json
import bitly_api
import re

MAX_CHAR_LIMIT = 140

bitly_login = "o_78h31d9njm"
bitly_key = "R_aeae9efa42d34ec596def38ccd7ead98"
# bitly_client_id = "689e696796798a795b6721eeda7155e0cdd7ecaf"
# bitly_secret = "99d3756705db3022f25d0bcbdff6e1086849a8b3"
generic_token = "d2bb3e68f8c2ee1ec322a4799b4a8a094e226c2a"
consumer_key = "cjUlJQr8ukJpwSMnq5w1EQkbE"
consumer_secret = "dckLfSNywCSIecVGjW8rbLMUlLAfKjzDFwUQTrduLOiTKiGGFZ"
access_token = "4718417858-D0UbpDi30tN0ahxPPX0EZZuBStTp2HtKGdPN5AK"
access_token_secret = "bCvERaLZCWgLy8AmEAP6in6b1v6bLhFrYSFyMGZcA9wu0"

from tweepy import OAuthHandler
from tweepy import API
from tweepy import TweepError

# This is a basic listener that just prints received tweets to stdout.


class Bot(object):

    """ An individual Bot conversation
    """

    default_endpoint = 'http://data.gov.au'
    purpose = re.compile(
        r'.*(what)[\w\s]+(is)[\w\s]+(purpose).*',
        re.IGNORECASE
    )

    def __init__(self, **kwargs):
        # Copy in all data
        self.text = ''
        super(Bot, self).__init__()
        for arg, value in kwargs.items():
            setattr(self, arg, value)

        # Set up response
        self.response = {
            'text': '',
        }

        # Run chat
        # We need to replace links in slack with the default values, if given
        # since slack does data.gov.au -> <http://data.gov.au|data.gov.au>
        # so we regexp it and replace

        # Strip text of first token which is always 'databot'
        try:
            tokens = self.text.split()[1:]
        except IndexError:
            return self.respond('Hello @{0.user_name}, how can I ?')

        if Bot.purpose.search(" ".join(tokens)):
            return self.respond("@{0.user_name} I serve butter, I mean data.")
        # First token should be 'find', if not, just say hello
        first = tokens.pop(0)
        if first != 'find':
            return self.respond(
                "Sorry @{0.user_name}, I didn't understand that")
        else:
            self.respond('Thanks @{0.user_name}. ')

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

        # Check endpoint is valid
        redir_url = requests.get(self.endpoint)
        if redir_url.ok:
            self.endpoint = redir_url.url
        else:
            return self.respond("\nLooks like something's borked at "
                                "{0.short_endpoint}, you're on your own!")
        # Make sure we can query the endpoint
        self.short_endpoint = self.endpoint
        if not self.endpoint.startswith('http'):
            self.endpoint = 'http://' + self.endpoint
        self.endpoint = self.endpoint + 'api/3/action'
        self.bit_bot = bitly_api.Connection(access_token=generic_token)
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
                description = "No desc for file"
            link = self.shorten_urls(result['resources'][0]['url'])
            fmt = result['resources'][0]['format']
            if fmt in ('', None):
                fmt = 'in an unknown format'
            else:
                if any(fmt.startswith(v) for v in 'aeiou'):
                    fmt = 'an ' + fmt + ' file'
                else:
                    fmt = 'a ' + fmt + ' file'

            # Post message
            template = u'{0}. '
            self.respond(template.format(
                link))
        except IndexError:
            self.respond(
                "Hmm, I've found a resource here"
                " but can't parse it. Moving on...")

    def query(self, tokens):
        """ Run a query
        """
        # Jas@20/1/16 - If a token has a - in front, it is removed and placed
        # in filter_out
        filter_out = {t.lstrip('-') for t in tokens if t.startswith('-')}
        tokens = {t for t in tokens if not t.startswith('-')}

        # Run the query
        query = '+'.join(tokens)

        # Jas@20/1/16 - I made rows : 100,
        # to give the user more details abot what's being
        # filtered with search terms.
        data = {'q': query, 'rows': 100}
        query_response = requests.get(
            self.endpoint + '/package_search', params=data)

        # Jas@20/1/16 - Some changes to this condition statement,
        # to reflect filtered results
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
                self.respond(("{0} results.").format(count))
                if filtered_count > 0:
                    self.respond(("From the top 100 results, "
                                  "I removed {0} with these"
                                  " terms: {1}. ").format(
                        filtered_count,
                        ', '.join(filter_out)))
                    self.respond(
                        "Here's the top result from the filtered list: ")
                else:
                    self.respond("Top link: ")
                if len(results) > 0:
                    self.send_file_info(results[0])
                else:
                    self.respond("nil")
                more_link = (
                    "{0.short_endpoint}dataset?q={1}"
                    "&sort=extras_harvest_portal+asc,+score+desc").format(
                    self,
                    query)
                short_more = self.shorten_urls(more_link)
                self.respond(
                    ('Want more? {0}.'.format(short_more)))
            else:
                self.respond(("Sorry, I couldn't find anything"
                              " on '{0}' at {{0.short_endpoint}}.").format(
                    '+'.join(tokens)))
        else:
            self.respond("Looks like something's borked at "
                         "{0.endpoint}, you're on your own!")

    def random(self):
        """ Return a random dataset
        """
        self.respond("I can't let you do that @{0.user_name}.")

    def changed(self):
        """
        Return the datasets which have changed recently
        """
        changed_response = requests.get(
            self.endpoint + '/recently_changed_packages_activity_list')

        # Respond with a few answers
        if changed_response.ok:
            results = changed_response.json()
            count = results['result']['count']
            self.respond(("I found {0} results which have recently changed "
                          "at {{0.short_endpoint}}, "
                          "here's the top ten:").format(count))
            for result in results['result']['results']:
                self.send_file_info(result)
        else:
            self.respond("Looks like something's borked at "
                         "{0.short_endpoint}, you're on your own!")

    def shorten_urls(self, url):
        "Returns a shortend url using the bitly api"
        try:
            return self.bit_bot.shorten(url)['url']
        except bitly_api.BitlyError as e:
            print e
            self.respond("Whoops looks like a failed at "
                         "getting a shortend link. Blame Bill. {0}".format(
                             url))

if __name__ == '__main__':

    # This handles Twitter authetification and the connection to Twitter
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    # TODO
    # Really need to loop through data instead of just getting
    # first value

    last_id = None
    while True:
        if last_id is None:
            data = api.mentions_timeline(count=1)[0]
        else:
            data = api.mentions_timeline(since_id=last_id, count=1)[0]
        if data:
            try:
                bot = Bot(text=data.text, user_name=data.user.screen_name)
                api.update_status(
                    status=bot.response['text'],
                    in_reply_to_status_id=data.id
                )
                last_id = data.id
            except TweepError as e:
                print e.args
        sleep(20)
