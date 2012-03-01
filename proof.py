import time

from pyrally.client import RallyAPIClient
from pyrally import settings
from pyrally.models import Story, Artifact, Task, User

rac = RallyAPIClient(settings.RALLY_USERNAME,
                     settings.RALLY_PASSWORD,
                     settings.BASE_URL)

rac.rally_access.default_cache_timeout = 0
print settings.BASE_URL, settings.RALLY_USERNAME

def sort_by_rank(story_a, story_b):
    return cmp(story_a.Rank, story_b.Rank)

from pyrally.models import get_query_clauses
stories = Story.get_all_in_iteration("Sprint 101")
stories.sort(sort_by_rank)
for s in stories:
    print s.FormattedID, s.Name, s.Rank, s.KanbanState

story_to_change = stories[1]
if story_to_change.KanbanState == 'In Development':
    state = 'In RC review'
else:
    state = 'In Development'
story_to_change.KanbanState = state

del story_to_change.rally_data['Rank']
story_to_change.update_rally()

print 'AFTER'
stories = Story.get_all_in_iteration("Sprint 101")
stories.sort(sort_by_rank)
for s in stories:
    print s.FormattedID, s.Name, s.Rank, s.KanbanState


# clause_1 = get_query_clauses([
#                 'WorkProduct.Owner = "alex.couper@glassesdirect.com"',
#                 'WorkProduct.Owner = "carles.barrobes@glassesdirect.com"',
#                 'WorkProduct.Owner = "james.carr-saunders@glassesdirect.com"',
#                 'WorkProduct.Owner = "orne.brocaar@glassesdirect.com"',
#                 'WorkProduct.Owner = "paula.norris@glassesdirect.com"',
#                    ], ' or ')

# clause_1 = get_query_clauses([
#                 'WorkProduct.Owner = "daniel.watkins@glassesdirect.com"',
#                 'WorkProduct.Owner = "fabrizio.romano@glassesdirect.com"',
#                 'WorkProduct.Owner = "ondrej.kohout@glassesdirect.com"',
#                    ], ' or ')

# # clause_1 = get_query_clauses([
# #                 'WorkProduct.Owner = "mark.henwood@glassesdirect.com"',
# #                 'WorkProduct.Owner = "phil.osmond@glassesdirect.com"',
# #                 'WorkProduct.Owner = "rob.lofthouse@glassesdirect.com"',
# #                 'WorkProduct.Owner = "mide.ojikutu@glassesdirect.com"',
# #                 'WorkProduct.Owner = "mark.wood@glassesdirect.com"',
# #                    ], ' or ')
# full_clause = get_query_clauses(['Iteration.Name = "Sprint 18"', clause_1])
# print full_clause
# story = Story.get_by_formatted_id('us98')
# print story.rally_url

# (Iteration.Name = "Sprint 18") and (((WorkProduct.Owner = "daniel.watkins@glassesdirect.com") or (WorkProduct.Owner = "fabrizio.romano@glassesdirect.com")) or (WorkProduct.Owner = "ondrej.kohout@glassesdirect.com"))

# (Iteration.Name = "Sprint 18") and (((((WorkProduct.Owner = "mark.henwood@glassesdirect.com") or (WorkProduct.Owner = "phil.osmond@glassesdirect.com")) or (WorkProduct.Owner = "rob.lofthouse@glassesdirect.com")) or (WorkProduct.Owner = "mide.ojikutu@glassesdirect.com")) or (WorkProduct.Owner = "mark.wood@glassesdirect.com"))
# clauses = ['DisplayName = "Alex C"']
# owner = User.get_all(clauses)[0]
# # Now add a task to the story in Rally
# task = Task({'Name': 'First task {0}'.format(time.ctime()),
#              'Status': 'Defined',
#              'WorkProduct': story.ref,
#              'Owner': owner.ref})
# task.update_rally()

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
