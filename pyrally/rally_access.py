import urllib2
import simplejson
import time
import contextlib
from collections import defaultdict


class UnexpectedResponse(Exception):
    pass

ACCESSOR = None

MEM_CACHE = defaultdict(dict)
"""Dictionary of request_type: {request: (response, time_of_stored_request)}"""
CACHE_TIMEOUT = 120
"""Seconds to store an item in memory for, before it needs refreshing"""


def get_accessor(username=None, password=None, rally_base_url=None):
    global ACCESSOR
    if not ACCESSOR:
        if not (username and password and rally_base_url):
            raise Exception('RallyAccessor must be established'
                            ' before accessing without username, password and'
                            'rally_base_url\n'
                            'Try instantiating a client object first.')
        ACCESSOR = RallyAccessor(username, password, rally_base_url)
    return ACCESSOR


class RallyAccessor(object):

    def __init__(self, username, password, base_url):
        """
        Set up access to rally with the given url and credentials.

        :param username:
            The username to login to Rally with.

        :param password:
            The password used to access Rally with the given username.

        :param base_url:
            The URL used to access the Rally API. This should be one of:
                * https://rally1.rallydev.com/
                * https://community.rallydev.com/
                * https://trial.rallydev.com/
        """
        self.base_url = base_url
        self.api_url = '{0}slm/webservice/1.29/'.format(self.base_url)
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(
                None, base_url, username, password
        )
        self.auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        self.cache_timeouts = {}
        self.default_cache_timeout = CACHE_TIMEOUT

    def make_url_safe(self, url):
        """
        Make the given url safe for use against the Rally API.

        :param url:
            The url we want to make safe.

        :returns:
            A new url string with all " ", "(", ")" and '"' characters replaced
            by html % characters.
        """
        return url.replace(' ', '%20')\
                  .replace('(', '%28')\
                  .replace(')', '%29')\
                  .replace('"', '%22')

    def set_cache_timeout(self, cache_key, timeout):
        """Set the timeout for the given cache_key.

        :param cache_key:
            The cache key to set a timeout for.

        :param timeout:
            The time in seconds to keep items in ``cache_key`` for.
        """
        self.cache_timeouts[cache_key.lower()] = timeout

    def delete_from_cache(self, cache_key, cache_index):
        """Delete the item from the cache.

        :param cache_key:
            The key to look up in order to find the ``cache_index``.

        :param cache_index:
            The index of within ``cache_key`` to delete.

        This does not raise a KeyError if the object can't be found.
        """
        try:
            del MEM_CACHE[cache_key.lower()][cache_index]
        except KeyError:
            pass

    def get_cacheable_info(self, url):
        """
        Return interesting bits of the url for caching.

        :param url:
            The url being cached.

        :returns:
            A tuple of cache_key (ie the API object type) and cache_lookup
            (the id of the object, or the query string if not a specific
            object.)
        """
        url_of_interest = url.replace('.js', '').split(self.api_url)[1]
        if '/' in url_of_interest:
            # We've got an object request like this:
            # hierarchicalrequirement/5128087372.js
            lookup_tuple = url_of_interest.split('/')
            cache_key = lookup_tuple[0]
        elif '?' in url_of_interest:
            # We've got ourselves a query like this:
            # hierarchicalrequirement.js?query=%28FormattedID%20=%20%22us20%
            # 22%29&pagesize=100&start=1&fetch=true
            lookup_tuple = url_of_interest.split('?')
            # Different cache_key because we want to be able to cache these
            # separately with different timeouts to the actual object type
            cache_key = '{0}_query'.format(lookup_tuple[0])

        cache_lookup = lookup_tuple[1]

        return cache_key, cache_lookup

    def get_from_cache(self, url):
        """
        Attempt to get the url result from the cache.

        :returns:
            The contents stored against the cache_key, cache_lookup in the
            cache, derived from the url (if it has
            not expired). Otherwise returns False.
        """
        cache_key, cache_lookup = self.get_cacheable_info(url)

        cache_timeout = self.cache_timeouts.get(cache_key,
                                                self.default_cache_timeout)

        data, access_time = MEM_CACHE[cache_key].get(cache_lookup, (None, 0))
        if data and time.time() - access_time < cache_timeout:
            return data
        return False

    def set_to_cache(self, url, data):
        """
        Set the url in the cache to have this data.

        :param url:
            The url to index the ``data`` against. This url will be broken
            down into ``cache_key``, ``cache_lookup`` items and indexed.

        :param data:
            The data to store against the broken down url.
        """
        cache_key, cache_lookup = self.get_cacheable_info(url)
        MEM_CACHE[cache_key][cache_lookup] = (data, time.time())

    def make_api_call(self, url, full_url=False, method='GET', data=None):
        """
        Make a call against the API at the given url.

        :param url:
            The url to make the call against. Note that this will be converted
            before being used through
            :py:meth:`~pyrally.rally_access.RallyAccessor.make_url_safe`.

        :param full_url:
            Boolean. If ``True``, it is assumed that the url contains the stem
            of the API call as opposed to a relative one in the case of
            ``False``.

        :param method:
            String describing HTTP method to use. One of ``GET``, ``POST``
            or ``DELETE``.

        :param data:
            Dictionary. Used as part of a ``PUT`` or ``POST`` request.

        :returns:
            The JSON data as returned by the API converted into python
            dictionary objects. This is done either by looking in the cache,
            or by actually getting it from the server.
        """
        url = self.make_url_safe(url)
        if not full_url:
            full_url = '{0}{1}'.format(self.api_url, url)
        else:
            full_url = url

        print full_url

        if method == 'GET':
            data = self.get_from_cache(full_url)
            if not data:
                request = urllib2.Request(full_url)
                data = self._get_json_response(request)
                self.set_to_cache(full_url, data)
            return data
        elif method == 'POST':
            encoded_data = simplejson.dumps(data)
            request = urllib2.Request(full_url, encoded_data,
                                 {'Content-Type': 'application/json'})
        elif method == 'DELETE':
            request = urllib2.Request(full_url)
            request.get_method = lambda: 'DELETE'

        return self._get_json_response(request)

    def _get_json_response(self, request_obj):
        """Call urlopen with a request object and return a dictionary.

        :param request_obj:
            A ``urllib2.request`` object to call opener.open with.

        :returns:
            A dictionary loaded with json response content from Rally.
        """
        opener = urllib2.build_opener(self.auth_handler)
        with contextlib.closing(opener.open(request_obj)) as open_url:
            response = open_url.read()
        # Reset the auth_handler as urllib2 doesn't seem to want to behave
        # properly.
        self.auth_handler.retried = 0
        return simplejson.loads(response)
