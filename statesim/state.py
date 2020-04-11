#

import logging

import numpy as np

logger = logging.getLogger(__name__)

class State(object):
    """ Represents a state, including its power, borders, and alliances.
    """

    def __init__(self, name, power, misperception=0.2):
        self.name = name
        self.power = power
        self.misperception = misperception
        self.border = []
        self.alliance = []
        self.conquered = None

    def scan_targets(self):
        """
        """
        power_diff = [self.power - i.power for i in self.border]
        target_ix = np.argmax(power_diff)
        return self.border[target_ix]

    def seek_allies(self, against):
        """ Returns list of states that border the state specified as against,
        such that it is the minimal winning coalition.
        """
        against_power_est = self.estimate_power(against) + self.estimate_power(against.alliance)
        bordering_states = [i for i in against.border if i != self and i not in self.alliance]

        if len(bordering_states) == 0:
            return None

        bordering_states.sort()
        potential_alliance = [self, bordering_states[0]]
        for i in bordering_states[1:]:
            i_power_est = self.estimate_power(i)
            if self.power + i_power_est + sum(potential_alliance) < against_power_est:
                potential_alliance.append(i)
            else:
                break
        return potential_alliance

    def propose_alliance(self, to, alliance, against):
        """ State proposes to another state, to, a potential alliance,
        alliance, against another state, against. to decides based on
        the estimated power of the coalition relative to state.
        """
        print('%s proposes alliance to %s' % (self, to)),
        logger.info('%s proposes alliance to %s' % (self, to))
        if against.alliance == []:
            against_est_power = to.estimate_power(against)
        else:
            against_est_power = to.estimate_power(against.alliance)
        
        alliance_est_power = to.estimate_power(alliance)

        if alliance_est_power > against_est_power:
            self.alliance.append(to)
            to.alliance.append(self)
            logger.info('%s has accepted offer of alliance from %s' % (to, self))
            return True
        else:
            logger.info('%s has rejected offer of alliance from %s' % (to, self))
            return False

    def estimate_power(self, state):
        """ Calculate state's estimation of another, using
        config settings to calculate error.
        """
        if type(state) == State:
            estimate = state.power * np.random.normal(loc=1, scale=self.misperception)
            logger.info('%s estimates %s power as %s' % (self, state, round(estimate, 2)))
            return estimate
        elif type(state) == list:
            if state == []:
                logger.info('%s estimates %s power as %s' % (self, state, 0))
                return 0
            else:
                estimate = sum([i.power * np.random.normal(loc=1, scale=self.misperception) for i in state])
                logger.info('%s estimates %s power as %s' % (self, state, round(estimate, 2)))
                return estimate


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
