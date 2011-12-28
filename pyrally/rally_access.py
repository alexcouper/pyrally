import urllib2
import simplejson
import time


class UnexpectedResponse(Exception):
    pass

ACCESSOR = None

MEM_CACHE = {}
"""Dictionary of request: (response, time_of_stored_request)"""
CACHE_TIMEOUT = 120
"""Seconds to store an item in memory for, before it needs refreshing"""


def get_accessor(username=None, password=None):
    global ACCESSOR
    if not ACCESSOR:
        if not (username and password):
            raise Exception('RallyAccessor must be established'
                            ' before accessing without username and password. '
                            'Try instantiating a client object first.')
        ACCESSOR = RallyAccessor(username, password)
    return ACCESSOR


class RallyAccessor(object):

    def __init__(self, username, password):
        self.base_url = 'https://rally1.rallydev.com/'
        self.api_url = '{0}slm/webservice/1.29/'.format(self.base_url)
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(
                None, 'https://rally1.rallydev.com/', username, password
        )
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        self.cache_timeout = CACHE_TIMEOUT

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

    def make_api_call(self, url, full_url=False):
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
        data, access_time = MEM_CACHE.get(full_url, (None, 0))
        if not data or time.time() - access_time > self.cache_timeout:
            response = urllib2.urlopen(full_url).read()
            data = simplejson.loads(response)
            MEM_CACHE[full_url] = (data, time.time())
        return data
