#
from itertools import combinations, islice
import logging

import numpy as np

logger = logging.getLogger(__name__)

class State(object):
    """ Represents a state, including its power, borders, and alliances.
    """

    def __init__(self, name, power, misperception=0.2):
        self.name = name
        self.misperception = misperception
        self.power = power
        self.power0 = self.power * np.random.normal(loc=1,
                                                    scale=self.misperception)
        self.border = []
        self.alliance = [self]
        self.conquered = None

    def scan_targets(self):
        """
        """
        power_diff = [self.power - i.power for i in self.border]
        target_ix = np.argmax(power_diff)
        target = self.border[target_ix]
        return target if target != self and target.power < self.power else None

    def seek_allies(self, against):
        """ Returns list of states that border the state specified as against,
        such that it is the minimal winning coalition.
        """
        against_power_est = self.estimate_alliance(against)

        all_alliances = []
        potential_allies = [i for i in against.border if i not in self.alliance and i not in against.alliance]
        for i in range(len(potential_allies) + 1):
            counter = 0
            for c in combinations(potential_allies, i):
                if counter < 100:
                    c_list = [j for j in c]
                    all_alliances.append(self.alliance + c_list)
                    counter += 1
                else:
                    break

        # Add in existing alliance

        # n = min(len(all_alliances), 1000)
        # alliances_power = np.array([sum(i) for i in all_alliances[0:n]])
        alliances_power = np.array([sum(i) for i in all_alliances])

        winning_alliances = np.where(alliances_power <= sum(against.alliance), np.inf, alliances_power)

        ix = np.argmin(winning_alliances)
        mwc = all_alliances[ix]

        return mwc


        ###
        # bordering_states = [i for i in against.border if i not in self.alliance and i not in against.alliance]

        # if len(bordering_states) == 0:
        #     return []

        # bordering_states.sort()
        # # potential_alliance = [self, bordering_states[0]]
        # potential_alliance = self.alliance + [bordering_states[0]]
        # for i in bordering_states[1:]:
        #     i_power_est = self.estimate_power(i)
        #     if sum(potential_alliance) < against_power_est:
        #         potential_alliance.append(i)
        #     else:
        #         break
        # return potential_alliance
        ####

    def propose_alliance(self, to, alliance, against):
        """ State proposes to another state, to, a potential alliance,
        alliance, against another state, against. to decides based on
        the estimated power of the coalition relative to state.
        """
        print('%s proposes alliance to %s' % (self, to)),
        logger.info('%s proposes alliance to %s' % (self, to))

        if to == self:
            raise ValueError('%s cannot propose alliance to itself' % self)

        if to in against.alliance:
            logger.info('%s is already allied, rejects offer of alliance from %s' % (to, self))
            return False

        # Estimate enemy alliance
        against_est_power = to.estimate_alliance(against)

        # Estimate proposed alliance -- to should not estimate its own power
        other_allies = [i for i in alliance if i != to]
        alliance_est_power = to.estimate_alliance(other_allies) + to.power

        if alliance_est_power > against_est_power:
            logger.info('%s has accepted offer of alliance from %s' % (to, self))
            self.alliance.append(to)
            to.alliance.append(self)
            return True
        else:
            logger.info('%s has rejected offer of alliance from %s' % (to, self))
            return False

    def estimate_power(self, state):
        """ Calculate state's estimation of another, using
        config settings to calculate error.
        """
        # if type(state) == State:
        estimate = state.power * np.random.normal(loc=1, scale=self.misperception)
        logger.info('%s estimates %s power as %s' % (self, state, round(estimate, 2)))
        return estimate
        # elif type(state) == list:
        #     if state == []:
        #         logger.info('%s estimates %s power as %s' % (self, state, 0))
        #         return 0
        #     else:
        #         estimate = sum([i.power * np.random.normal(loc=1, scale=self.misperception) for i in state])
        #         logger.info('%s estimates %s power as %s' % (self, state, round(estimate, 2)))
        #         return estimate

    def estimate_alliance(self, state):
        """ Estimate power of multiple states at once, including proposed alliances.
        """
        if type(state) == State:
            allies = state.alliance
        elif type(state) == list:
            allies = state

        allies_power = [self.estimate_power(i) for i in allies]
        return sum(allies_power)


    def __repr__(self):
        return 'State %s (power=%s)' % (self.name, round(self.power, 2))

    def __add__(self, x):
        """
        """
        return self.power + x

    def __radd__(self, x):
        """
        """
        if x == 0:
            return self.power
        else:
            return self.__add__(x)

    def __eq__(self, x):
        """ Evaluate = operator on states' power.
        """
        if self.power == x.power:
            return True
        else:
            return False

    def __ne__(self, x):
        """
        """
        if self.power != x.power:
            return True
        else:
            False

    def __lt__(self, x):
        """
        """
        if self.power < x.power:
            return True
        else:
            return False

    def __le__(self, x):
        """
        """
        if self.power <= x.power:
            return True
        else:
            return False

    def __gt__(self, x):
        """
        """
        if self.power > x.power:
            return True
        else:
            return False

    def __ge__(self, x):
        """
        """
        if self.power >= x.power:
            return True
        else:
            return False
