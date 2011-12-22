from mock import patch
from nose.tools import assert_equal

from pyrally.client import RallyAPIClient

TEST_RA_CLIENT = RallyAPIClient('username', 'password')


@patch('pyrally.client.get_accessor')
def test_initialisation(get_accessor):
    """Test that ``RallyAPIClient`` initialises correctly.

    Tests that :py:func:`~pyrally.rally_access.get_accessor` is called with
    the appropriate arguments.
    """
    RallyAPIClient('mock_username', 'mock_password')

    assert_equal(get_accessor.call_args[0], ('mock_username', 'mock_password'))


@patch('pyrally.client.Artifact')
def test_get_all_entities(Artifact):
    """Test that ``get_all_entities`` calls the expected method.

    Tests that :py:meth:`~pyrally.client.RallyAPIClient.get_all_entities`
    returns the value returned by method
    :py:meth:`~pyrally.models.Artifact.get_all`.
    """
    result = TEST_RA_CLIENT.get_all_entities()
    assert_equal(result, Artifact.get_all.return_value)


@patch('pyrally.client.Defect')
@patch('pyrally.client.Story')
def test_get_all_in_kanban_state_gets_stories_and_defects(Story, Defect):
    """Test that ``get_all_in_kanban_state`` calls the expected methods.

    Tests :py:meth:`~pyrally.client.RallyAPIClient.get_all_in_kanban_state`.

    Tests that:
        * calls Story.get_all_in_kanban_state
        * calls Defect.get_all_in_kanban_state
        * returns a dictionary with all kanban data.
    """
    result = TEST_RA_CLIENT.get_all_in_kanban_state('state_name')

    assert_equal(Story.get_all_in_kanban_state.call_count, 1)
    assert_equal(Defect.get_all_in_kanban_state.call_count, 1)
    assert_equal(result,
                 {'stories': Story.get_all_in_kanban_state.return_value,
                  'defects': Defect.get_all_in_kanban_state.return_value})


@patch('pyrally.client.Story')
def test_get_story_by_name(Story):
    """Test that ``get_story_by_name`` calls the expected method.

    Tests that :py:meth:`~pyrally.client.RallyAPIClient.get_story_by_name`
    returns the value returned by method
    :py:meth:`~pyrally.models.Story.get_by_name`
    """
    result = TEST_RA_CLIENT.get_story_by_name('mock_name')
    assert_equal(Story.get_by_name.call_args[0][0], 'mock_name')
    assert_equal(result, Story.get_by_name.return_value)


@patch('pyrally.client.Defect')
def test_get_defect_by_name(Defect):
    """Test that ``get_defect_by_name`` calls the expected method.

    Tests that :py:meth:`~pyrally.client.RallyAPIClient.get_defect_by_name`
    returns the value returned by method
    :py:meth:`~pyrally.models.Defect.get_by_name`
    """
    result = TEST_RA_CLIENT.get_defect_by_name('mock_name')
    assert_equal(Defect.get_by_name.call_args[0][0], 'mock_name')
    assert_equal(result, Defect.get_by_name.return_value)


@patch('pyrally.client.Artifact')
def test_get_entity_by_name(Artifact):
    """Test that ``get_entity_by_name`` calls the expected method.

    Tests that :py:meth:`~pyrally.client.RallyAPIClient.get_entity_by_name`
    returns the value returned by method
    :py:meth:`~pyrally.models.Artifact.get_by_name`
    """
    result = TEST_RA_CLIENT.get_entity_by_name('mock_name')
    assert_equal(Artifact.get_by_name.call_args[0][0], 'mock_name')
    assert_equal(result, Artifact.get_by_name.return_value)

