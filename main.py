#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main script to run StateSim

# TODO: handle borders if state is out
# TODO: propose.alliance: Needs to consider allies: target's existing allies, and include states allies in calculations
# TODO: If state,power < target.power, what happens?
# TODO: Likelihood of victory may need to lower?
# TODO: War damage is pretty small

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

world = InternationalSystem(config=config)


# Randomly select state
state = world.random_state()

# State looks for a target state to pick on
target = state.scan_targets()
state_est_target = state.estimate_power(target)

# Targetted state looks for allies
# Target estimates the power of the iniating state
target_est_state = target.estimate_power(state)
if target.power <= target_est_state:
    target_potential_alliance = target.seek_allies(against=state)
    # TODO: Fix this, also does not have self in .alliance !
    for ally in target_potential_alliance[1:]:
        target.propose_alliance(to=ally, alliance=target_potential_alliance,
                                against=state)

# Initiator's rejoinder to target's diplomacy
# IF target fails to get alliances, go for war:
if len(target.alliance) == 0:
    war = world.war(state, target)
# initiator compares power with target coalition's allinace's power
elif state.power > state_est_target + state.estimate_power(target.alliance):
    war = world.war(state, target)
else:
    state_potential_alliance = state.seek_allies(against=target)
    for ally in state_potential_alliance[1:]:
        state.propose_alliance(to=ally, alliance=state_potential_alliance,
                               against=target)
    # if such a coalition was needed and does not exist, end conflict and break
    if len(state.alliance) == 0:
        world.end_turn(); break
    # if all states poposed to join, then continue to war; else back down
    elif len(state.alliance) < len(state_potential_alliance)-1:
        world.end_turn(); break

# Target gets one last chance for allies and diplomacy
# If target+alliance has more powerful, do nothing
# if target+alliance is not as powerful, more alliance building
target_est_alliance = target.estimate_power(target.alliance)
target_est_state_alliance = target.estimate_power(state) + target.estimate_power(state.alliance)
if (target.power + target_est_alliance) <= target_est_state_alliance:
    target_potential_alliance = target.seek_allies(against=state)
    target_potential_alliance = [i for i in target_potential_alliance if i not in target.alliance]
    for ally in target_potential_alliance[1:]:
        target.propose_alliance(to=ally, alliance=target_potential_alliance,
                                against=state)

# TODO: if this new alliance is bigger back down

war = world.war(state, target)
world.assess_war_damage(war)
world.end_turn()

####
# THIS WORKS!
import scipy.integrate as integrate
p0 = 5
p1 = 3
sigma = 2.0

const = 1 / np.sqrt(3.14*sigma)
# f <- function(x) exp( -(x/sigma)^2 )
f = lambda x: np.exp( -1 * np.square(x/sigma) )
area = integrate.quad( f, -np.inf, np.log(p0 / p1) )
area[0] * const
######


if __name__ == '__main__':

    config = yaml.full_load( open('config.yaml') )

    world = InternationalSystem(config=config)

    for i in range(1, config.niter):

        print('Iteration no. %s' % i)

        # Randomly select state
        state = world.random_state()

        # State looks for a target state to pick on
        target = state.scan_targets()

        # Targetted state looks for allies
        if target.power <= state.power:
            target_potential_allies = target.seek_allies()
            world.offer_alliance(originator=target,
                                 recipients=target_potential_allies)

        # Original, initiating state looks for allies
        if state.power < sum( [i.power for i in target.allies] ):
            state_potential_allies = state.seek_allies()
            world.offer_alliance(originator=state,
                                 recipients=state_potential_allies)

        # Calculate final balance of power, war or peace ensues
        if sum( [i.power for i in state.allies] ) > sum( [i.power for i in target.allies] ):
            # War!
            war = world.war(state, target)
            world.assess_war_damage(war)

        world.end_turn()