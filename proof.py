from pyrally.settings import KANBAN_STATES
from pyrally.client import RallyAPIClient


rac = RallyAPIClient()

for kb_state in KANBAN_STATES:
    objs = rac.get_all_in_kanban_state(kb_state)
    print kb_state, objs
