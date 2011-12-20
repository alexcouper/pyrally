from pyrally.settings import KANBAN_STATES
from pyrally.client import RallyAPIClient
from pyrally import settings
from pyrally.models import Story

rac = RallyAPIClient(settings.RALLY_USERNAME, settings.RALLY_PASSWORD)

all_stories = Story.get_all()
print len(all_stories)

story = rac.get_story_by_name('us524')
print story
print story.Owner.DisplayName
story = rac.get_story_by_name('us124')
print story.__dict__
print story.Owner
print story.title

dict_obj = rac.get_all_in_kanban_state('In QA Testing')
print dict_obj

story = rac.get_entity_by_name('us524')
defect = rac.get_entity_by_name('de92')
print story.title
print defect.title

story = rac.get_story_by_name('us524')
print story.Description
print story.title
print story.FormattedID
print story.Blocked

defect = rac.get_defect_by_name('de92')
print defect.Description
print defect.title
print defect.FormattedID
print defect.tasks
print defect.Blocked

all_entities = rac.get_all_entities()
print len(all_entities)

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
