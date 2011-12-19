import urllib2
import simplejson

from pyrally import settings


class UnexpectedResponse(Exception):
    pass

ACCESSOR = None


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

    def make_url_safe(self, url):
        return url.replace(' ', '%20')\
                  .replace('(', '%28')\
                  .replace(')', '%29')\
                  .replace('"', '%22')

    def make_api_call(self, url, full_url=False):
        url = self.make_url_safe(url)
        if not full_url:
            full_url = '{0}{1}'.format(self.api_url, url)
        else:
            full_url = url
        data = urllib2.urlopen(full_url).read()
        return simplejson.loads(data)

