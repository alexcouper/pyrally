import time

from mock import patch, Mock
from nose.tools import assert_equal, assert_raises, assert_false

from pyrally.rally_access import RallyAccessor, get_accessor, MEM_CACHE


@patch('pyrally.rally_access.ACCESSOR')
@patch('pyrally.rally_access.RallyAccessor')
def test_get_accessor_returns_created_accessor_if_available(RallyAccessor,
                                                            ACCESSOR):
    """
    Test ``get_accessor`` returns created.

    Test that :py:func:`~pyrally.rally_access.get_accessor` returns the created
    accessor if it is available.
    """
    assert_equal(get_accessor(), ACCESSOR)
    assert_false(RallyAccessor.called)


@patch('pyrally.rally_access.ACCESSOR', None)
@patch('pyrally.rally_access.RallyAccessor')
def test_get_accessor_creates_accessor_if_not_already_created(RallyAccessor):
    """
    Test ``get_accessor`` returns created.

    Test that :py:func:`~pyrally.rally_access.get_accessor` creates
    and returns a :py:class:`~pyrally.rally_access.RallyAccessor` object if it
    has not already been created.
    """
    assert_equal(get_accessor('uname', 'pword', 'base_url'),
                 RallyAccessor.return_value)
    assert_equal(RallyAccessor.call_args[0], ('uname', 'pword', 'base_url'))


@patch('pyrally.rally_access.ACCESSOR', None)
@patch('pyrally.rally_access.RallyAccessor')
def test_get_accessor_raises_exception_if_not_created_and_no_uname_password(
                                                                RallyAccessor):
    """
    Test ``get_accessor`` raises Exception.

    Test that :py:func:`~pyrally.rally_access.get_accessor` raises an Exception
    if global ACCESSOR is None and called with no username and password
    arguments.
    """
    assert_raises(Exception, get_accessor)
    assert_false(RallyAccessor.called)


def test_make_url_safe():
    """Test that :py:meth:`.RallyAccessor.make_url_safe` works correctly."""
    my_accessor = RallyAccessor('uname', 'pword', 'base_url')
    for url, expected_outcome in [
                                    (' ', "%20"),
                                    ('(', "%28"),
                                    (')', "%29"),
                                    ('"', "%22"),
                                    ('(Hello = "Fred")',
                                     '%28Hello%20=%20%22Fred%22%29')]:
        assert_equal(my_accessor.make_url_safe(url), expected_outcome)


@patch('pyrally.rally_access.urllib2')
@patch('pyrally.rally_access.MEM_CACHE')
def test_make_api_call_full_url_cached(MEM_CACHE, urllib2):
    """
    Test ``make_api_call`` with full, cached url.

    Tests that :py:meth:`~.RallyAccessor.make_api_call`:
        * looks in the cache first and does not make a urllib call.
        * uses the url given without amendments.
        * makes the url given safe.
    """
    my_accessor = RallyAccessor('uname', 'pword', 'base_url')
    my_accessor.make_url_safe = Mock()
    my_accessor.make_url_safe.return_value = 'safe-url'
    MEM_CACHE.get.return_value = ('Data', time.time())

    response = my_accessor.make_api_call('some-url', full_url=True)

    assert_equal(response, 'Data')
    assert_equal(my_accessor.make_url_safe.call_args[0], ('some-url',))
    assert_equal(MEM_CACHE.get.call_args[0], ('safe-url', (None, 0)))
    assert_false(urllib2.urlopen.called)


@patch('pyrally.rally_access.urllib2')
@patch('pyrally.rally_access.simplejson')
def test_make_api_call_partial_url_not_cached(simplejson, urllib2):
    """
    Test ``make_api_call`` with partial url, not cached.

    Tests that :py:meth:`~.RallyAccessor.make_api_call`:
        * makes a call to the API via urllib.
        * prepends the api_url to the partial url.
        * makes the url given safe.
    """
    MEM_CACHE.clear()

    my_accessor = RallyAccessor('uname', 'pword', 'base_url')
    my_accessor.api_url = 'http://dummy_url/'

    my_accessor.make_url_safe = Mock()
    my_accessor.make_url_safe.return_value = 'safe-url'
    urllib2.urlopen().read.return_value = 'RAW_DATA'
    simplejson.loads.return_value = 'python_dict'

    response = my_accessor.make_api_call('some-url', full_url=False)

    assert_equal(response, 'python_dict')
    assert_equal(my_accessor.make_url_safe.call_args[0], ('some-url',))
    assert_equal(urllib2.urlopen.call_args[0], (urllib2.Request.return_value,))
    assert_equal(simplejson.loads.call_args[0], ('RAW_DATA',))
