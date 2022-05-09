import pytest

from gradescope_mean.assign_list import *

columns = ['skip me', 'HW1 - max points', 'hw1', 'HW2 - max points', 'hw2']


@pytest.fixture
def ass_list():
    return AssignmentList(columns)


class TestAssignmentList:
    def test_init(self, ass_list):
        ass_list_exp = ['hw1', 'hw2']
        assert ass_list == ass_list_exp

    def test_match(self, ass_list):
        ass_list.match('  hw1  ', max_pts=False) == 'hw1'

        ass_list.match('hw2', max_pts=True) == 'hw2 - max points'

        with pytest.raises(AssignmentNotFoundError):
            ass_list.match('hw')
            ass_list.match('ghost assignment')

    def test_match(self, ass_list):
        s_assign_tup_exp = ('hw1', 'hw2')
        s_assign_tup = ass_list.match_multi(s_assign='hw')
        assert s_assign_tup == s_assign_tup_exp
