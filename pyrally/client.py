from pyrally.models import Story, Defect, Artifact
from pyrally.rally_access import get_accessor


class RallyAPIClient(object):

    def __init__(self, username, password, base_url):
        self.rally_access = get_accessor(username, password, base_url)

    def get_all_entities(self):
        """
        Get all stories, defects and tasks.

        :returns:
            A list of ``BaseRallyModel`` inherited objects.
        """
        return Artifact.get_all()

    def get_all_in_kanban_states(self, kanban_states):
        """
        Get all stories and defects in the given ``kanban_state``.

        :param kanban_state:
            A list of kanban states to search on.

        :returns:
            A dictionary containing keys for ``stories`` and ``defects``, and
            values of lists of associated ``Story`` and ``Defect`` objects.
        """
        stories = Story.get_all_in_kanban_states(kanban_states)
        defects = Defect.get_all_in_kanban_states(kanban_states)
        return {'stories': stories, 'defects': defects}

    def get_story_by_formatted_id(self, story_id):
        """
        Return the story with the id ``story_id``.

        :param story_id:
            The USXXX story id of the story.

        :returns:
            A ``Story`` object.
        """
        return Story.get_by_formatted_id(story_id)

    def get_defect_by_formatted_id(self, defect_id):
        """
        Return the defect with the id ``defect_id``.

        :param defect_id:
            The DEXXX defect id of the defect.

        :returns:
            A ``Defect`` object.
        """
        return Defect.get_by_formatted_id(defect_id)

    def get_entity_by_formatted_id(self, entity_id):
        """
        Return the entity with the id ``entity_id``.

        :param entity_id:
            The YYXXX id of the story/defect/task.

        :returns:
            A ``BaseRallyModel`` inheritted object, or None if no artifacts
            could be found.
        """
        return Artifact.get_by_formatted_id(entity_id)
