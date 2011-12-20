from pyrally.models import Story, Defect, Artifact
from pyrally.rally_access import get_accessor


class RallyAPIClient(object):

    def __init__(self, username, password):
        self.rally_access = get_accessor(username, password)

    def get_all_entities(self):
        """
        Get all stories, defects and tasks.

        :returns:
            A list of ``BaseRallyModel`` inherited objects.
        """
        return Artifact.get_all()

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

    def get_entity_by_name(self, entity_name):
        """
        Return the entity with the name ``entity_name``.

        :param entity_name:
            The YYXXX id of the story/defect/task.

        :returns:
            A ``BaseRallyModel`` inheritted object, or None if no artifacts
            could be found.
        """
        return Artifact.get_by_name(entity_name)
