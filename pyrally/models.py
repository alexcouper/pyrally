"""
For the latest API information go to
https://rally1.rallydev.com/slm/doc/webservice/
"""
from pyrally.rally_access import get_accessor

from pyrally.register import register_type, API_OBJECT_TYPES


class ReferenceNotFoundException(Exception):
    pass


def get_query_clauses(clauses, joiner=' and '):
    """
    Return clauses used for querying objects from the API.

    :param clauses:
        A list of clause strings to be joined in the correct fashion using
        ``joiner`` and brackets

    :param: joiner:
        This should either be `` and `` or `` or ``. All clauses in ``clause``
        are joined together using this operator.

    :returns:
        A single query_clause string containing all of ``clauses``.
    """
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
            # If the class being defined does not inherit from BaseRallyModel
            # We don't want to register it.
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
        self.rally_data = data_dict

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
                try:
                    return object_class.create_from_ref(rally_item['_ref'])
                except ReferenceNotFoundException:
                    return None
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
    def create_from_ref(cls, reference):
        """Create an instance of ``cls`` by getting data for ``reference``.

        :param reference:
            The full url reference to make an api call with.

        :returns:
            A populated :py:exc:`~pyrally.models.BaseRallyModel` inheriting
            instance which matches the reference.

        :raises:
            A :py:class:`~pyrally.models.ReferenceNotFoundException` if we get
            any error back from the API.
        """
        response = get_accessor().make_api_call(reference, True)
        errors = response.get('OperationResult', {'Errors': []}).get('Errors')
        if errors:
            msg = """
        Failure: {0}-{1}: {2}.
        If you called this directly, check that you've got the right reference
        number.
        Otherwise, it's highly likely that the reference was left hanging
        around in Rally after a delete (eg if a User was deleted).
        """.format(cls, reference, errors)
            raise ReferenceNotFoundException(msg)
        return cls(response[cls.rally_name])

    @classmethod
    def get_all(cls, clauses=None):
        """
        Return all the items for the rally class.

        :param clauses:
            Optional parameter of a list of clauses to be ``and`` ed together
            by :py:func:`~pyrally.models.get_query_clauses`.

        :returns:
            A list of :py:class:`~pyrally.models.BaseRallyModel` inheriting
            objects.
        """
        if clauses:
            query_string = get_query_clauses(clauses)
        else:
            query_string = ''
        results = cls.get_all_results_for_query(query_string)

        return cls.convert_from_query_result(results, full_objects=True)

    @classmethod
    def get_all_results_for_query(cls, query_string):
        """
        Return all the results for the given query.

        Increment the ``start`` argument until entire result set has been
        retrieved and return just the results.

        :param query_string:
            The query to filter results by. If None, all results are returned
            for the object.

        :returns:
            A list of full object results (ie fetch=true is set in the API
            GET)
        """
        more_pages = True
        start_index = 1
        all_results = []
        while more_pages:
            query_result_dict = cls._get_results_page(query_string,
                                                      start_index)
            all_results.extend(query_result_dict['Results'])
            start_index = (query_result_dict['PageSize'] +
                           query_result_dict['StartIndex'])

            total_results = query_result_dict['TotalResultCount']
            more_pages = len(all_results) < total_results

        return all_results

    @classmethod
    def _get_results_page(cls, query_string, start_index=1):
        """
        Get a page of results for the query given.

        :param query_string:
            The string to get results for. If ``None``, or ``""``, no query
            is passed in and all objects for the class will be returned.

        :param start_index:
            The 1-based offset to fetch from. A pagesize of 100 is returned.

        :returns:
            The QueryResult entity as returned by the API, containing at most
            100 results.

        :raises:
            Exception if ['QueryResult']['Errors'] contains anything.
        """
        query_arg = ""
        if query_string:
            query_arg = "query=({0})&".format(query_string)

        url = "{0}.js?{1}pagesize=100&start={2}&fetch=true".format(
                        cls.rally_name.lower(), query_arg, start_index)
        query_result_dict = get_accessor().make_api_call(url)
        if query_result_dict['QueryResult']['Errors']:
            raise Exception('Errors in query: {0}'.format(
                             query_result_dict['QueryResult']['Errors']))
        return query_result_dict['QueryResult']

    @classmethod
    def convert_from_query_result(cls, results, full_objects=False):
        """Convert a set of Rally results into python objects.

        :param results:
            An iterable of results from the Rally API.

        :param full_objects:
            Boolean. If ``True``, ``results`` is assumed to contain full
            objects as returned by the API when ``fetch=True`` is included in
            the URL. If ``False``, the full object data is fetched using
            :py:meth:`~pyrally.models.BaseRallyModel.create_from_ref`.

        :returns:
            A list of full :py:class:`~pyrally.models.BaseRallyModel`
            inheriting python objects.
        """
        converted_results = []
        for result in results:
            object_class = API_OBJECT_TYPES.get(result['_type'],
                                                BaseRallyModel)
            if full_objects:
                new_obj = object_class(result)
            else:
                new_obj = object_class.create_from_ref(result['_ref'])
            converted_results.append(new_obj)
        return converted_results

    @classmethod
    def get_by_name(cls, name):
        """Return all the objects by the given name.

        :param name:
            The name to search for. The get is performed by setting
            FormattedID=``name`` in the url.

        :returns:
            A single :py:class:`~pyrally.models.BaseRallyModel` inheriting
            object with the FormattedID = name. Or ``None`` if one cannot
            be found.
        """
        clauses = ['FormattedID = "{0}"'.format(name)]
        all_objects = cls.get_all(clauses)
        # Strangely, this returns for us444: de444, ta444 and us444.
        for obj in all_objects:
            if obj.FormattedID.lower() == name.lower():
                return obj
        return None

    @property
    def title(self):
        """Property for getting the title of an object.

        :returns:
            The attribute found in the key ``_refObjectName`` in the data
            back from the API
        """
        return self._refObjectName


class Artifact(BaseRallyModel):
    rally_name = 'Artifact'


class Task(BaseRallyModel):
    rally_name = 'Task'

    @classmethod
    def get_all_for_story(cls, story_id):
        """
        Get all the tasks for the given ``story_id``.

        :param story_id:
            The USXXX or DEXXX parent ID of a task to search for.

        :returns:
            A list of ``Task`` objects, as returned by get_all
        """
        clauses = ['WorkProduct.FormattedId = "{0}"'.format(story_id)]
        return cls.get_all(clauses)


class Story(BaseRallyModel):
    rally_name = 'HierarchicalRequirement'
    sub_objects_dynamic_loader = {'tasks': 'Tasks', 'children': 'Children'}

    @classmethod
    def get_all_in_kanban_state(cls, kanban_state):
        """
        Get all the stories in the given kanban_state.

        :param kanban_state:
            The kanban state to search on.

        :returns:
            A list of ``Story`` objects, as returned by get_all
        """
        clauses = ['KanbanState = "{0}"'.format(kanban_state)]
        return cls.get_all(clauses)


class Defect(BaseRallyModel):
    rally_name = "Defect"
    sub_objects_dynamic_loader = {'tasks': 'Tasks'}

    @classmethod
    def get_all_in_kanban_state(cls, kanban_state):
        """
        Get all the defects in the given kanban_state.

        :param kanban_state:
            The kanban state to search on.

        :returns:
            A list of ``Defect`` objects, as returned by get_all
        """
        clauses = ['KanbanState = "{0}"'.format(kanban_state)]
        return cls.get_all(clauses)


class User(BaseRallyModel):
    rally_name = 'User'


class Iteration(BaseRallyModel):
    rally_name = 'Iteration'
