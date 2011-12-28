from mock import Mock
from nose.tools import assert_equal

from pyrally.models import Task


def get_inherited_class_object():
    class MockTaskModel(Task):
        rally_name = 'FakeRallyName'
    return MockTaskModel


def test_get_all_for_story():
    """
    Test :py:meth:`~.Task.get_all_for_story`.

    Test that:
        * Uses the correct clause
        * Returns the result of get_all using the clause.
    """
    MockTask = get_inherited_class_object()
    MockTask.get_all = Mock()

    response = MockTask.get_all_for_story('USXXX')

    assert_equal(response, MockTask.get_all.return_value)
    assert_equal(MockTask.get_all.call_args[0],
                (['WorkProduct.FormattedId = "USXXX"'],))
