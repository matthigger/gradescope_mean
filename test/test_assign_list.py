import pytest

from gradescope_mean.assign_list import *

columns = ['skip me', 'H W 1 - max points', 'hw1', 'HW2 - max points', 'hw2']


@pytest.fixture
def ass_list():
    return AssignmentList(columns)


class TestAssignmentList:
    def test_normalize(self):
        assert AssignmentList.normalize('  A B C 1 2 3') == 'abc123'

    def test_init(self, ass_list):
        ass_list_exp = ['H W 1', 'HW2']
        assert ass_list == ass_list_exp

    def test_match(self, ass_list):
        ass_list.match('  hw1  ') == 'hw1'

        with pytest.raises(AssignmentNotFoundError):
            ass_list.match('hw')
            ass_list.match('ghost assignment')

    def test_match_iter(self, ass_list):
        s_assign_exp = ['H W 1', 'HW2']
        s_assign = sorted(ass_list.match_iter(s_assign='hw'))
        assert s_assign == s_assign_exp
