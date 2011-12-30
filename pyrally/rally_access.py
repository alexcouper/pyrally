import urllib2
import simplejson
import time
import contextlib


class UnexpectedResponse(Exception):
    pass

ACCESSOR = None

MEM_CACHE = {}
"""Dictionary of request: (response, time_of_stored_request)"""
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
        print 'creating'
        self.base_url = base_url
        self.api_url = '{0}slm/webservice/1.29/'.format(self.base_url)
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(
                None, base_url, username, password
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
            data, access_time = MEM_CACHE.get(full_url, (None, 0))
            if not data or time.time() - access_time > self.cache_timeout:
                request = urllib2.Request(full_url)
                data = self._get_json_response(request)
                MEM_CACHE[full_url] = (data, time.time())
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
            A ``urllib2.request`` object to call urlopen with.

        :returns:
            A dictionary loaded with json response content from Rally.
        """
        with contextlib.closing(urllib2.urlopen(request_obj)) as open_url:
            response = open_url.read()
        return simplejson.loads(response)
