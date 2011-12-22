from nose.tools import assert_equal, assert_true

from pyrally.models import (BaseRallyModel, Iteration, User, Defect, Story,
                            Task, Artifact)


def test_class_definitions():
    """
    Test that all model classes are set up correctly.

    They should inherit from :py:class:`~pyrally.models.BaseRallyModel` and
    define the correct ``rally_name``.
    """
    for class_type, rally_type in [(Iteration, 'Iteration'),
                                   (User, 'User'),
                                   (Defect, 'Defect'),
                                   (Story, 'HierarchicalRequirement'),
                                   (Task, 'Task'),
                                   (Artifact, 'Artifact')]:
        obj = class_type({})
        assert_true(isinstance(obj, BaseRallyModel))
        assert_equal(obj.rally_name, rally_type)
