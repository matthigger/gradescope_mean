from collections import namedtuple
from math import isclose

from gradescope_mean.get_mean_drop_low import *

TestCase = namedtuple('TestCase', ['perc', 'weight', 'drop_n', 'mean_exp'])


def test_get_mean_drop_low():
    test_case_list = [
        TestCase(perc=[1, .9, .8],
                 weight=[1, 1, 1],
                 drop_n=0,
                 mean_exp=.9),
        TestCase(perc=[1, .9, .8],
                 weight=[1, 0, 0],
                 drop_n=0,
                 mean_exp=1),
        TestCase(perc=[1, .9, .8],
                 weight=[1, 1, 1],
                 drop_n=1,
                 mean_exp=.95),
        TestCase(perc=[1, .8, np.nan],
                 weight=[1, 1, 1],
                 drop_n=0,
                 mean_exp=.9),
        TestCase(perc=[1, .8, np.nan],
                 weight=[1, 1, 1],
                 drop_n=1,
                 mean_exp=1),
        TestCase(perc=[1, .8, .8],
                 weight=[1, 1, 10],
                 drop_n=1,
                 mean_exp=.9)]

    for idx, test_case in enumerate(test_case_list):
        mean = get_mean_drop_low(perc=test_case.perc,
                                 weight=test_case.weight,
                                 drop_n=test_case.drop_n)
        assert isclose(mean, test_case.mean_exp), f'fail case: {idx}'
