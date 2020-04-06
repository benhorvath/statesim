# Main script to run StateSim

from statesim.system import InternationalSystem
from statesim.state import State


if __name__ == '__main__':

    sim_config = yaml.load('config.yaml')
    logger = logger()

    world = InternationalSystem(config=sim_config)

    for i in range(1, sim_config.niter):

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