"""
For the latest API information go to
https://rally1.rallydev.com/slm/doc/webservice/
"""
from pyrally.rally_access import get_accessor

API_OBJECT_TYPES = {}


def register_type(class_type):
    global API_OBJECT_TYPES
    API_OBJECT_TYPES[class_type.rally_name] = class_type


def get_query_clauses(clauses, joiner=' and '):
    if len(clauses) == 1:
        return '{0}'.format(clauses[0])
    else:
        total_clauses = []
        first_two = clauses[:2]
        for clause in first_two:
            formatted_clause = '({0})'.format(get_query_clauses([clause]))

            total_clauses.append(formatted_clause)

        new_clauses = []
        new_clauses.append(joiner.join(total_clauses))
        if len(clauses) > 2:
            new_clauses.extend(clauses[2:])
        return get_query_clauses(new_clauses, joiner)


class RegisterModels(type):
    """A metaclass used for registering all BaseRallyModel subclasses"""
    def __init__(cls, name, bases, attrs):
        try:
            if BaseRallyModel not in bases:
                return
        except NameError:
            return
        register_type(cls)


class BaseRallyModel(object):

    __metaclass__ = RegisterModels
    sub_objects_dynamic_loader = {}
    """A dictionary of ``property_name``: ``key_name``.

    Where ``property_name`` is the name of a property on the class which
    refers to a dynamically loaded list of items found in the ``rally_data``
    key ``key_name``.
    """

    def __init__(self, data_dict):
        self._full_sub_objects = {}
        self.rally_data = {}
        self.rally_data = data_dict[self.rally_name]

    def __getattribute__(self, attr_name):
        """Patch the default __getattribute__ call to be better for us.

        Rather than *only* looking at the __dict__ of the object do determine
        attribute resolution, improve so that:

            * Attributes are looked at in the underlying ``rally_data`` stored
              against the object.

                * If found in this data and it is a dictionary, load a new
                  python object up with the data.
                * Otherwise, just return the data.

            * If not found there, attributes are looked at in
              ``sub_objects_dynamic_loader``. This is a dictionary of
              ``property_name`` to ``rally_data`` key. If ``attr_name`` exists
              in this mapping, the corresponding data is dynamically loaded and
              returned.
            * If neither of these yield results, return the standard object
              __getattribute__ result.
        """
        # Filter out the attributes we require to make decisions in this
        # method. Otherwise, we'll get "Maximum recursion depth" errors.
        if attr_name in ['rally_data', 'sub_objects_dynamic_loader',
                         '_full_sub_objects']:
            return object.__getattribute__(self, attr_name)

        rally_data = object.__getattribute__(self, 'rally_data')
        if attr_name in rally_data:
            rally_item = rally_data[attr_name]
            if isinstance(rally_item, dict) and '_ref' in rally_item:
                rally_name = rally_item['_type']
                object_class = API_OBJECT_TYPES.get(rally_name, BaseRallyModel)
                return object_class.create_from_ref(rally_item['_ref'])
            else:
                return rally_item
        else:
            # If it is not in the rally data, let's check if we're trying to
            # access an auto-loading attribute.
            if attr_name in self.sub_objects_dynamic_loader:

                if attr_name not in self._full_sub_objects:
                    rally_data_equivalent = \
                                    self.sub_objects_dynamic_loader[attr_name]
                    self._full_sub_objects[attr_name] = []
                    for skeleton in self.rally_data.get(rally_data_equivalent,
                                                        []):
                        rally_name = skeleton['_type']
                        object_class = API_OBJECT_TYPES.get(rally_name,
                                                            BaseRallyModel)
                        self._full_sub_objects[attr_name].append(
                                    object_class.create_from_ref(
                                                             skeleton['_ref']))
                return self._full_sub_objects[attr_name]
            return object.__getattribute__(self, attr_name)

    @classmethod
    def create_from_query_result(cls, query_result_dict):
        if query_result_dict['QueryResult']['Errors']:
            raise Exception('Errors in query: {0}'.format(
                                query_result_dict['QueryResult']['Errors']))
        results = []
        for result in query_result_dict['QueryResult']['Results']:
            object_class = API_OBJECT_TYPES.get(result['_type'],
                                                BaseRallyModel)
            results.append(object_class.create_from_ref(result['_ref']))
        return results

    @classmethod
    def create_from_ref(cls, reference):
        response = get_accessor().make_api_call(reference, True)
        return cls(response)

    @classmethod
    def get_all_by_attrs(cls, clauses):
        query_string = get_query_clauses(clauses)
        url = "{0}.js?query=({1})".format(cls.rally_name.lower(), query_string)
        return cls.create_from_query_result(get_accessor().make_api_call(url))

    @classmethod
    def get_by_name(cls, story_name):
        clauses = ['FormattedID = "{0}"'.format(story_name)]
        return cls.get_all_by_attrs(clauses)[0]

    @property
    def name(self):
        return self._refObjectName


class Task(BaseRallyModel):
    rally_name = 'Task'

    @classmethod
    def get_all_for_story(cls, story_id):
        clauses = ['WorkProduct.FormattedId = "{0}"'.format(story_id)]
        return cls.get_all_by_attrs(clauses)


class Story(BaseRallyModel):
    rally_name = 'HierarchicalRequirement'
    sub_objects_dynamic_loader = {'tasks': 'Tasks'}

    @classmethod
    def get_all_in_kanban_state(cls, kanban_state):
        clauses = ['KanbanState = "{0}"'.format(kanban_state)]
        return cls.get_all_by_attrs(clauses)


class Defect(BaseRallyModel):
    rally_name = "Defect"
    sub_objects_dynamic_loader = {'tasks': 'Tasks'}

    @classmethod
    def get_all_in_kanban_state(cls, kanban_state):
        clauses = ['KanbanState = "{0}"'.format(kanban_state)]
        return cls.get_all_by_attrs(clauses)


class User(BaseRallyModel):
    rally_name = 'User'


class Iteration(BaseRallyModel):
    rally_name = 'Iteration'


class Artifact(BaseRallyModel):
    rally_name = 'Artifact'

    @classmethod
    def get_by_name(cls, name):
        """Get an artifact by name.

        :param name:
            The name of the artifact (eg US323 or de12)

        :returns:
            A BaseRallyModel inherited object containing the details of the
            relevant matching object, or ``None`` if one couldn't be found.
        """
        clauses = ['FormattedID = "{0}"'.format(name)]
        all_artifacts = cls.get_all_by_attrs(clauses)
        # Strangely, this returns for us444: de444, ta444 and us444.
        for artifact in all_artifacts:
            if artifact.FormattedID.lower() == name.lower():
                return artifact
        return None

