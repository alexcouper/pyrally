from mock import Mock
from nose.tools import assert_equal

from pyrally.models import HierarchicalRequirement


def get_inherited_class_object():
    class MockStoryModel(HierarchicalRequirement):
        rally_name = 'FakeRallyName'
    return MockStoryModel


def test_get_all_in_kanban_state():
    """
    Test :py:meth:`~.HierarchicalRequirement.get_all_in_kanban_state`.

    Test that:
        * Uses the correct clause
        * Returns the result of get_all using the clause.
    """
    MockStory = get_inherited_class_object()
    MockStory.get_all = Mock()
    response = MockStory.get_all_in_kanban_state('Kanban State Name')

    assert_equal(response, MockStory.get_all.return_value)
    assert_equal(MockStory.get_all.call_args[0],
                (['KanbanState = "Kanban State Name"'],))
