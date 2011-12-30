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
    print 'in test'
    rally_access.MEM_CACHE = {}
    RallyAPIClient(settings.RALLY_USERNAME,
                   settings.RALLY_PASSWORD,
                   settings.BASE_URL)

    # Create a story
    s = Story({'DefectStatus': "NONE",
                'ScheduleState': "Defined",
                'TaskStatus': 'NONE',
                'TestCaseStatus': 'NONE',
                'Name': 'Dummy Story Auto Created',
                })
    s.update_rally()
    # Check it has been created
    print s.title, s.Name, s.FormattedID
    assert_true('US' in s.FormattedID)
    assert_equal(s.title, 'Dummy Story Auto Created')
    assert_true(s.ref)
    # Edit the story
    s.update(Name="Changed Story Name")
    s.update_rally()
    # Check that the edit has taken place
    # Delete the cache so we can be sure we're getting it from Rally.
    rally_access.MEM_CACHE = {}
    s2 = Story.get_by_name(s.FormattedID)
    assert_equal(s2.Name, 'Changed Story Name')
    # Delete the story
    print s2.FormattedID
    s2.delete()
    # Delete the cache so we can be sure we're getting it from Rally.
    rally_access.MEM_CACHE = {}
    # Check the story no longer exists.
    s3 = Story.get_by_name(s.FormattedID)
    assert_equal(s3, None)
