from django.test import TestCase
import pytest


class ThinsliceTests(TestCase):

    def func(self, x):
        '''
        Demo function to test the running of tests
        '''
        return x + 1

    def test_answer(self):
        '''
        Failing test
        '''
        # assert self.func(3) == 5
        assert self.func(3) != 5

    def test_thinslice(self):
        '''
        Passing test
        '''
        assert self.func(4) == 5
