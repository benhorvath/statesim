# alliance test


import logging
import sys
import yaml

from statesim.system import InternationalSystem
from statesim.state import State

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(levelname)s | %(asctime)s | %(name)s | %(''message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

config = yaml.full_load( open('config.yaml') )

state1 = State(name=1, power=10, misperception=0)
state4 = State(name=4, power=6, misperception=0)
state6 = State(name=6, power=7, misperception=0)

state2 = State(name=2, power=5, misperception=0)
state3 = State(name=3, power=6, misperception=0)
state5 = State(name=5, power=8, misperception=0)
state7 = State(name=7, power=10, misperception=0)

state1.border = [state2, state4, state6]
state4.border = [state1]
state6.border = [state1]

state2.border = [state1, state3, state5, state7]
state3.border = [state1]
state5.border = [state1]
state7.border = [state1]

# state1 selects state2 as target
state = state1
target = state2

# Target sees state1 is more powerful, so moves to come up with alliance -- should be state4
target_potential_alliance = target.seek_allies(against=state)
for ally in target_potential_alliance:
    if ally != target:
        target.propose_alliance(to=ally,
                                alliance=target_potential_alliance,
                                against=state)

# state1 will try get 3 to join
state_potential_alliance = state.seek_allies(against=target)
for ally in state_potential_alliance[1:]:
    state.propose_alliance(to=ally, alliance=state_potential_alliance,
                           against=target)

# Finally, target will successfully ally with state 6
# PROBLEM: WHY IS STATE 7 REJECTING THIS ALLIANCE? -- because it's not including target's first allies!
target_potential_alliance = target.seek_allies(against=state)
new_proposal = [i for i in target_potential_alliance if i not in target.alliance]
for ally in new_proposal:
    target.propose_alliance(to=ally, alliance=target_potential_alliance,
                            against=state)

# Test war

