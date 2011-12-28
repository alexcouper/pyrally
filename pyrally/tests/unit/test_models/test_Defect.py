from mock import Mock
from nose.tools import assert_equal

from pyrally.models import Defect


def get_inherited_class_object():
    class MockDefectModel(Defect):
        rally_name = 'FakeRallyName'
    return MockDefectModel


def test_get_all_in_kanban_state():
    """
    Test :py:meth:`~.Defect.get_all_in_kanban_state`.

    Test that:
        * Uses the correct clause
        * Returns the result of get_all using the clause.
    """
    MockDefect = get_inherited_class_object()
    MockDefect.get_all = Mock()
    response = MockDefect.get_all_in_kanban_state('Kanban State Name')

    assert_equal(response, MockDefect.get_all.return_value)
    assert_equal(MockDefect.get_all.call_args[0],
                (['KanbanState = "Kanban State Name"'],))
