import pytest

from mean_scope.assign_list import *

columns = ['skip me', 'HW1 - max points', 'hw1', 'HW2 - max points', 'hw2']


@pytest.fixture
def ass_list():
    return AssignmentList(columns)


class TestAssignmentList:
    def test_init(self, ass_list):
        ass_list_exp = ['hw1', 'hw2']
        assert ass_list == ass_list_exp

    def test_normalize(self, ass_list):
        ass_list.normalize('  hw1  ', max_pts=False) == 'hw1'

        ass_list.normalize('hw2', max_pts=True) == 'hw2 - max points'

        with pytest.raises(AssignmentNotFoundError):
            ass_list.normalize('hw')
            ass_list.normalize('ghost assignment')
