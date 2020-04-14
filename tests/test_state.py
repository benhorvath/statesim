# python -m unittest discover -v

import unittest

from statesim.state import State

class TestState(unittest.TestCase):

    def setUp(self):
        self.state1 = State(name=1, power=10, misperception=0)
        self.state4 = State(name=4, power=6, misperception=0)
        self.state6 = State(name=6, power=7, misperception=0)

        self.state2 = State(name=2, power=5, misperception=0)
        self.state3 = State(name=3, power=6, misperception=0)
        self.state5 = State(name=5, power=8, misperception=0)
        self.state7 = State(name=7, power=10, misperception=0)

        self.state1.border = [self.state2, self.state4, self.state6]
        self.state4.border = [self.state1]
        self.state6.border = [self.state1]

        self.state2.border = [self.state1, self.state3, self.state5,
                              self.state7]
        self.state3.border = [self.state1]
        self.state5.border = [self.state1]
        self.state7.border = [self.state1]

    def test_scan_targets1(self):
        self.assertEqual(self.state1.scan_targets(), self.state2)

    def test_scan_targets2(self):
        self.assertEqual(self.state2.scan_targets(), self.state3)

    def test_estimate_power(self):
        power_est = self.state2.estimate_power(self.state2)
        self.assertEqual(power_est, 5.0)

    def test_seek_allies1(self):
        allies = self.state2.seek_allies(self.state1)
        self.assertEqual(allies, [self.state2, self.state4])

    def test_seek_allies2(self):
        self.state1.alliance = [self.state1, self.state3]
        self.state2.alliance = [self.state2, self.state4]

        new_allies = self.state2.seek_allies(self.state1)
        expected = [self.state2, self.state4, self.state6]

        self.assertEqual(new_allies, expected)


