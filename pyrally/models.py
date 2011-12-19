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

    def __init__(self, data_dict):
        self.rally_data = {}
        self.rally_data = data_dict[self.rally_name]

    def __getattribute__(self, attr_name):
        if attr_name == 'rally_data':
            return object.__getattribute__(self, attr_name)

        rally_data = object.__getattribute__(self, 'rally_data')
        if attr_name in rally_data:
            if '_ref' in rally_data[attr_name]:
                rally_name = rally_data[attr_name]['_type']
                object_class = API_OBJECT_TYPES.get(rally_name, BaseRallyModel)
                return object_class.create_from_ref(
                                                 rally_data[attr_name]['_ref'])
            else:
                return rally_data[attr_name]
        else:
            return object.__getattribute__(self, attr_name)

    @classmethod
    def create_from_query_result(cls, query_result_dict):
        if query_result_dict['QueryResult']['Errors']:
            raise Exception('Errors in query')
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


class Task(BaseRallyModel):
    rally_name = 'Task'

    @classmethod
    def get_all_for_story(cls, story_id):
        clauses = ['WorkProduct.FormattedId = "{0}"'.format(story_id)]
        return cls.get_all_by_attrs(clauses)


class Story(BaseRallyModel):
    rally_name = 'HierarchicalRequirement'

    @classmethod
    def get_all_in_kanban_state(cls, kanban_state):
        clauses = ['KanbanState = "{0}"'.format(kanban_state)]
        return cls.get_all_by_attrs(clauses)


class Defect(BaseRallyModel):
    rally_name = "Defect"

    @classmethod
    def get_all_in_kanban_state(cls, kanban_state):
        clauses = ['KanbanState = "{0}"'.format(kanban_state)]
        return cls.get_all_by_attrs(clauses)


class User(BaseRallyModel):
    rally_name = 'User'


class Iteration(BaseRallyModel):
    rally_name = 'Iteration'

