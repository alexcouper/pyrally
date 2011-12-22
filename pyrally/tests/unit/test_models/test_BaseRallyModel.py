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

