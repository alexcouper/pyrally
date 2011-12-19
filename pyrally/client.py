from pyrally.models import Story, Defect
from pyrally.rally_access import get_accessor


class RallyAPIClient(object):

    def __init__(self, username, password):
        self.rally_access = get_accessor(username, password)

    def get_all_in_kanban_state(self, kanban_state):
        """
        Get all stories and defects in the given ``kanban_state``.

        :param kanban_state:
            The kanban state to search for.

        :returns:
            A dictionary containing keys for ``stories`` and ``defects``, and
            values of lists of associated ``Story`` and ``Defect`` objects.
        """
        stories = Story.get_all_in_kanban_state(kanban_state)
        defects = Defect.get_all_in_kanban_state(kanban_state)
        return {'stories': stories, 'defects': defects}

    def get_story_by_name(self, story_name):
        """
        Return the story with the name ``story_name``.

        :param story_name:
            The USXXX story id of the story.

        :returns:
            A ``Story`` object.
        """
        return Story.get_by_name(story_name)

    def get_defect_by_name(self, defect_name):
        """
        Return the defect with the name ``defect_name``.

        :param defect_name:
            The DEXXX defect id of the defect.

        :returns:
            A ``Defect`` object.
        """
        return Defect.get_by_name(defect_name)
