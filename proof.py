import time

from pyrally.client import RallyAPIClient
from pyrally import settings
from pyrally.models import Story, Artifact

rac = RallyAPIClient(settings.RALLY_USERNAME,
                     settings.RALLY_PASSWORD,
                     settings.BASE_URL)

print settings.BASE_URL, settings.RALLY_USERNAME

story = Story.get_by_formatted_id('us627')
print story.get_rally_url()


#stories = rac.get_all_in_kanban_states(['In QA Testing',
                                    #    'In Development'])['stories']
#print len(stories)
# def print_times(time_list):
#     last_t = 0
#     for i, t in enumerate(time_list):
#         if last_t:
#             print i, t-last_t
#         last_t = t

# Story.set_cache_timeout(100)

# times = []

# times.append(time.time())

# Story.get_all()

# times.append(time.time())

# Story.get_all()[0].tasks

# times.append(time.time())
# print_times(times)
# from pyrally.rally_access import MEM_CACHE
# print MEM_CACHE.keys()
# print rac.rally_access.cache_timeouts


#all_stories = Story.get_all()
#print len(all_stories)
#print Artifact.get_all_in_kanban_state('In Development')
#print Story.get_all_in_kanban_state('In Development')
# all_stories = Story.get_all()
# print len(all_stories)
# story = rac.get_story_by_name('us524')
# print story
# print story.Owner.DisplayName
# story = rac.get_story_by_name('us124')
# print story.__dict__
# print story.Owner
# print story.title

# dict_obj = rac.get_all_in_kanban_state('In QA Testing')
# print dict_obj

# story = rac.get_entity_by_name('us524')
# defect = rac.get_entity_by_name('de92')
# print story.title
# print defect.title

# story = rac.get_story_by_name('us524')
# print story.Description
# print story.title
# print story.FormattedID
# print story.Blocked

# defect = rac.get_defect_by_name('de92')
# print defect.Description
# print defect.title
# print defect.FormattedID
# print defect.tasks
# print defect.Blocked

# all_entities = rac.get_all_entities()
# print len(all_entities)

# print dict_obj
# for story in dict_obj['stories']:
#     print story.__dict__
#     print story.Tasks
#     print story.tasks
#     print story.mbfshipmenthandling
#     print story.mbfwarehousescreens

# for kb_state in KANBAN_STATES:
#     objs = rac.get_all_in_kanban_state(kb_state)
#     print kb_state, objs
