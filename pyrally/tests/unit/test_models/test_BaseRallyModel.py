from mock import patch, Mock
from nose.tools import assert_equal, assert_raises, assert_true, assert_false

from pyrally.models import BaseRallyModel, ReferenceNotFoundException


def get_inherited_class_object():
    class DummyRallyModel(BaseRallyModel):
        rally_name = 'FakeRallyName'
    return DummyRallyModel


@patch('pyrally.models.get_accessor')
def test_create_from_ref_no_errors(get_accessor):
    """Test :py:meth:`~.BaseRallyModel.create_from_ref` with no API errors.

    Test that ``create_from_ref`` makes a call to the Rally API and creates
    returns an instance of the class.
    """
    fake_rally_data = {'data': 'for_obj'}
    DummyClass = get_inherited_class_object()
    get_accessor().make_api_call.return_value = \
                                           {'FakeRallyName': fake_rally_data}
    obj = DummyClass.create_from_ref('test_reference')

    assert_true(isinstance(obj, DummyClass))
    assert_equal(obj.rally_data, fake_rally_data)


@patch('pyrally.models.get_accessor')
def test_create_from_ref_with_errors(get_accessor):
    """Test :py:meth:`~.BaseRallyModel.create_from_ref` with an API error.

    Test that ``create_from_ref`` raises a
    :py:class:`~pyrally.models.ReferenceNotFoundException` error when
    a call to the Rally API results in errors being returned.
    """
    DummyClass = get_inherited_class_object()

    get_accessor().make_api_call.return_value = \
                                           {'OperationResult':
                                                    {'Errors': ['Some error']}
                                            }
    assert_raises(ReferenceNotFoundException,
                  DummyClass.create_from_ref,
                  'test_reference')


@patch('pyrally.models.get_query_clauses')
def test_get_all_with_clauses(get_query_clauses):
    """
    Test :py:meth:`~.BaseRallyModel.get_all` with clauses passed in.

    Test that:
        * ``get_all`` calls ``get_query_clauses``
        * Uses the result to call ``get_all_results_for_query``
        * returns the set of objects as returned by
          ``convert_from_query_result``
    """
    DummyClass = get_inherited_class_object()

    get_query_clauses.return_value = 'mock_query'

    mock_get_all_results_for_query = Mock()
    mock_get_all_results_for_query.return_value = 'mock_results'
    mock_convert_from_query_result = Mock()
    mock_convert_from_query_result.return_value = 'mock_conversion'
    DummyClass.get_all_results_for_query = mock_get_all_results_for_query
    DummyClass.convert_from_query_result = mock_convert_from_query_result

    response = DummyClass.get_all('clauses')

    assert_equal(get_query_clauses.call_args[0][0], 'clauses')
    assert_equal(mock_get_all_results_for_query.call_args[0][0],
                 'mock_query')
    assert_equal(mock_convert_from_query_result.call_args[0][0],
                 'mock_results')
    assert_equal(response, 'mock_conversion')


@patch('pyrally.models.get_query_clauses')
def test_get_all_without_clauses(get_query_clauses):
    """
    Test :py:meth:`~.BaseRallyModel.get_all` with no clauses passed in.

    Test that:
        * ``get_all`` does not call ``get_query_clauses``
        * Calls ``get_all_results_for_query`` with a blank query.
        * returns the set of objects as returned by
          ``convert_from_query_result``
    """
    DummyClass = get_inherited_class_object()

    mock_get_all_results_for_query = Mock()
    mock_get_all_results_for_query.return_value = 'mock_results'
    mock_convert_from_query_result = Mock()
    mock_convert_from_query_result.return_value = 'mock_conversion'
    DummyClass.get_all_results_for_query = mock_get_all_results_for_query
    DummyClass.convert_from_query_result = mock_convert_from_query_result

    response = DummyClass.get_all()

    assert_false(get_query_clauses.called)
    assert_equal(mock_get_all_results_for_query.call_args[0][0],
                 '')
    assert_equal(mock_convert_from_query_result.call_args[0][0],
                 'mock_results')
    assert_equal(response, 'mock_conversion')


def test_get_all_results_for_query():
    """
    Test :py:meth:`~.BaseRallyModel.get_all_results_for_query`

    Test that:
        * Calls ``_get_results_page`` until all results are fetched.
        * Returns the total of all results pages.
    """
    results_pages = [{'Results': ['c'],
                      'PageSize': 2,
                      'StartIndex': 3,
                      'TotalResultCount': 3},
                     {'Results':['a', 'b'],
                      'PageSize': 2,
                      'StartIndex': 1,
                      'TotalResultCount': 3},
                     ]

    DummyClass = get_inherited_class_object()
    DummyClass._get_results_page = Mock()
    DummyClass._get_results_page.side_effect = lambda x, y: results_pages.pop()

    response = DummyClass.get_all_results_for_query('query_string')
    assert_equal(DummyClass._get_results_page.call_count, 2)
    assert_equal(response, ['a', 'b', 'c'])
    assert_equal(DummyClass._get_results_page.call_args[0][0], 'query_string')


@patch('pyrally.models.get_accessor')
def test__get_results_page_with_no_errors(get_accessor):
    """
    Test :py:meth:`~.BaseRallyModel._get_results_page` with no errors

    Test that:
        * Adds query in if present
        * Returns the ``QueryResult`` contents.
    """
    query_result = {'something': 'query_result', 'Errors': []}
    mock_api_response = {'QueryResult': query_result}
    get_accessor().make_api_call.return_value = mock_api_response
    expected_url = ('fakerallyname.js?query=(my_query_string)&'
                    'pagesize=100&start=1&fetch=true')
    DummyClass = get_inherited_class_object()

    response = DummyClass._get_results_page(query_string='my_query_string')

    assert_equal(get_accessor().make_api_call.call_count, 1)
    assert_equal(get_accessor().make_api_call.call_args[0][0], expected_url)
    assert_equal(response, query_result)


@patch('pyrally.models.get_accessor')
def test__get_results_page_with_errors(get_accessor):
    """
    Test :py:meth:`~.BaseRallyModel._get_results_page` with errors

    Test that:
        * Raises an ``Exception`` when ``[QueryResult][Errors]`` contains
          content
    """
    query_result = {'something': 'query_result', 'Errors': ['some_error']}
    mock_api_response = {'QueryResult': query_result}
    get_accessor().make_api_call.return_value = mock_api_response
    DummyClass = get_inherited_class_object()

    assert_raises(Exception, DummyClass._get_results_page, 'my_query_string')


@patch('pyrally.models.API_OBJECT_TYPES')
def test_convert_from_query_result_with_full_objects(API_OBJECT_TYPES):
    """
    Test :py:meth:`~.BaseRallyModel.convert_from_query_result` and full objects

    Test that:
        * Every result given is converted into the appropriate Python object
          determined by API_OBJECT_TYPES
        * ``create_from_ref`` is not called, meaning that no further API calls
          are required.
    """
    MockClass = Mock()
    API_OBJECT_TYPES.get.return_value = MockClass
    DummyClass = get_inherited_class_object()
    item_1 = {'_type': 'item_type',
              '_ref': 'mock_ref_1'}
    item_2 = {'_type': 'item_type',
              '_ref': 'mock_ref_2'}

    objects = DummyClass.convert_from_query_result([item_1, item_2], True)
    assert_equal(len(objects), 2)
    assert_equal(MockClass.call_count, 2)
    assert_false(MockClass.create_from_ref.called)
    assert_equal(API_OBJECT_TYPES.get.call_count, 2)
    assert_equal(API_OBJECT_TYPES.get.call_args[0],
                 ('item_type', BaseRallyModel))


@patch('pyrally.models.API_OBJECT_TYPES')
def test_convert_from_query_result_with_only_ref_objects(API_OBJECT_TYPES):
    """
    Test :py:meth:`~.BaseRallyModel.convert_from_query_result` with ref objects

    Test that:
        * Every result given is converted into the appropriate Python object
          determined by API_OBJECT_TYPES
        * ``create_from_ref`` is called for each reference
    """
    MockClass = Mock()
    API_OBJECT_TYPES.get.return_value = MockClass
    DummyClass = get_inherited_class_object()
    item_1 = {'_type': 'item_type',
              '_ref': 'mock_ref_1'}
    item_2 = {'_type': 'item_type',
              '_ref': 'mock_ref_2'}

    objects = DummyClass.convert_from_query_result([item_1, item_2], False)
    assert_equal(len(objects), 2)
    assert_false(MockClass.called)
    assert_equal(MockClass.create_from_ref.call_count, 2)
    assert_equal(API_OBJECT_TYPES.get.call_count, 2)
    assert_equal(API_OBJECT_TYPES.get.call_args[0],
                 ('item_type', BaseRallyModel))


def test_get_by_formatted_id():
    """
    Test :py:meth:`~.BaseRallyModel.get_by_formatted_id` works as expected

    Test that:
        * The correct clause is created and passed to ``get_all``.
        * Only one item is returned, the first returned back that truly
          matches the name.
    """
    DummyClass = get_inherited_class_object()

    mock_result_1 = Mock()
    mock_result_2 = Mock()
    mock_result_1.FormattedID = 'Some_Different_ID'
    mock_result_2.FormattedID = 'Some_ID'
    DummyClass.get_all = Mock()
    DummyClass.get_all.return_value = [mock_result_1, mock_result_2]

    result = DummyClass.get_by_formatted_id('Some_ID')

    assert_equal(result, mock_result_2)
    assert_equal(DummyClass.get_all.call_args[0],
                 (['FormattedID = "Some_ID"'],))


def test_get_by_formatted_id_no_match():
    """
    Test :py:meth:`~.BaseRallyModel.get_by_formatted_id` with no match.

    Test that:
        * The correct clause is created and passed to ``get_all``.
        * None is returned if there are no matches.
    """
    DummyClass = get_inherited_class_object()

    mock_result_1 = Mock()
    mock_result_2 = Mock()
    mock_result_1.FormattedID = 'Some_Different_ID'
    mock_result_2.FormattedID = 'Some_ID'
    DummyClass.get_all = Mock()
    DummyClass.get_all.return_value = []

    result = DummyClass.get_by_formatted_id('Some_ID')

    assert_equal(result, None)
    assert_equal(DummyClass.get_all.call_args[0],
                 (['FormattedID = "Some_ID"'],))


def test_title_property():
    """
    Test the ``title`` property of :py:class:`.BaseRallyModel`.
    """
    DummyClass = get_inherited_class_object()
    mock_instance = DummyClass({'_refObjectName': 'some ref'})
    assert_equal(mock_instance.title, 'some ref')
