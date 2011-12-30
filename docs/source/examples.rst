Getting Started
===============

``pyrally`` is now on PyPi.

To install it from the command line type:

$ pip install pyrally


Examples
========

Below are some examples of how to use pyrally.

1. Altering the name of a story

    .. code-block:: python

        >>> from pyrally import RallyAPIClient
        >>> from pyrally import Story
        >>> rac = RallyApiClient('username', 'password', 'https://rally1.rallydev.com/')
        >>> story = rac.get_story_by_name('us124')
        >>> story.update(Name='Why me?')
        >>> story.update_rally()

2. Deleting a story

    .. code-block:: python

        >>> s = Story.get_by_name('us123')
        >>> s.delete()

3. Creating a story

    .. code-block:: python

        >>> s = Story({'ScheduleState': "Defined", 'Name': 'Dummy Story Auto Created'})
        >>> s.update_rally()
