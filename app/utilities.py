""" file:   utilities.py
    author: Jess Robertson
    date:   Thursday 21 January 2016

    description: Utilities for databot
"""

import re

def replace_slack_links(string):
    """ Strips the http requests that slack sticks in strings
    """
    find_pattern = re.compile(r'(?<=\|)[.\w]*')
    replace_pattern = re.compile('<.*>')

    # Look for the match first
    match = replace_pattern.search(string)
    if match is not None:
        subsstr = find_pattern.search(string).group(0)
        return re.sub('<.*>', subsstr, string)
    else:
        return string

def get_values(obj=None):
    """ Gets all values from key-value pairs and lists from an arbitrarily
        nested object, munges into a big list.

        Handles arbitrarily nested lists and dictionaries. Useful for
        stripping keys out of JSON response values.

        Parameters:
            obj - the nested object to get values from

        Returns:
            a list of all the values found in the object
    """
    if obj is None:
        return []

    # Unwrap dictionaries
    if isinstance(obj, dict):
        values = []
        for _, value in obj.items():
            values.extend(get_values(value))
        return values

    # Unwrap lists
    elif isinstance(obj, list):
        values = []
        for list_value in obj:
            values.extend(get_values(list_value))
        return values

    # Everything else just gets returned for appending
    else:
        return [obj]

def filter_results_by_term(results_list, killwords):
    """ Filter results by removing those containing the given killwords

        Parameters:
            results_list - a list of dictionaries containing the response
                from a CKAN isinstance. Matching is case-insensitive.
            killwords - my name is a (list of) killing word(s)

        Returns:
            ok_results, n_killed - a list of accepable results, and the
                number of results killed
    """
    # Make sure we're case-insensitive
    killwords = [token.lower() for token in killwords]

    # Loop through and only keep results if they're palatable
    ok_results, n_killed = [], 0
    for res in results_list:
        # Get all the values in the result as a string
        result_string = ' '.join(str(v).lower() for v in get_values(res))

        # If there's no killwords, we keep it, otherwise we increase our
        # kill tally by one
        if not any([token in result_string for token in killwords]):
            ok_results.append(res)
        else:
            n_killed += 1

    return ok_results, n_killed
