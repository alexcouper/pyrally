from pyrally.settings import KANBAN_STATES
from pyrally.client import RallyAPIClient
from pyrally import settings


rac = RallyAPIClient(settings.RALLY_USERNAME, settings.RALLY_PASSWORD)

dict_obj = rac.get_all_in_kanban_state('In QA Testing')

story = rac.get_story_by_name('us524')
print story.Description
print story.name
print story.FormattedID
print story.Blocked

defect = rac.get_defect_by_name('de92')
print defect.Description
print defect.name
print defect.FormattedID
print defect.tasks
print defect.Blocked

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
