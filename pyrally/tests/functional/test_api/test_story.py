import time

from nose.tools import assert_true, assert_equal

from pyrally.client import RallyAPIClient
from pyrally.models import Story
from pyrally import rally_access
from pyrally import settings


def test_story_flow():
    """Test that we can do all the things we expect on a story."""
    if 'rally1' in settings.BASE_URL:
        raise Exception('This test should NOT be run against a live working '
                        'version of Rally. Please change your settings to '
                        'point to a community version (ie '
                        'community.rallydev.com).')
    rally_access.ACCESSOR = None
    rally_access.MEM_CACHE = {}
    RallyAPIClient(settings.RALLY_USERNAME,
                   settings.RALLY_PASSWORD,
                   settings.BASE_URL)

    story_name = 'Dummy Story Auto Created: {0}'.format(time.time())
    # Create a story
    s = Story({'DefectStatus': "NONE",
                'ScheduleState': "Defined",
                'TaskStatus': 'NONE',
                'TestCaseStatus': 'NONE',
                'Name': story_name,
                })
    s.update_rally()
    # Check it has been created
    assert_true('US' in s.FormattedID)
    assert_equal(s.title, story_name)
    assert_true(s.ref)
    # Edit the story
    new_name = "Changed Story Name: {0}".format(time.time())
    s.update(Name=new_name)
    s.update_rally()
    # Check that the edit has taken place
    # Delete the cache so we can be sure we're getting it from Rally.
    rally_access.MEM_CACHE = {}
    s2 = Story.get_by_formatted_id(s.FormattedID)
    assert_equal(s2.Name, new_name)
    # Delete the story
    s2.delete()
    # Delete the cache so we can be sure we're getting it from Rally.
    rally_access.MEM_CACHE = {}
    # Check the story no longer exists.
    s3 = Story.get_by_formatted_id(s.FormattedID)
    assert_equal(s3, None)
