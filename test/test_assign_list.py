import pytest

from gradescope_mean.assign_list import *

columns = ['skip me', 'H W 1 - max points', 'hw1', 'HW2 - max points', 'hw2']


@pytest.fixture
def ass_list():
    return AssignmentList(columns)


class TestAssignmentList:
    def test_normalize(self):
        assert normalize('  A B C 1 2 3') == 'abc123'

    def test_init(self, ass_list):
        ass_list_exp = ['hw1', 'hw2']
        assert ass_list == ass_list_exp

    def test_init_warns_prefix(self):
        with pytest.warns():
            l = [AssignmentList.MAX_PTS + s for s in
                 ('hw1', 'hw10', 'hw_another')]
            AssignmentList(l)

    def test_match(self, ass_list):
        assert ass_list.match('  hw1  ') == 'hw1'

        # ambiguous match (hw matches both hw1 and hw2)
        with pytest.raises(AssignmentNotFoundError):
            ass_list.match('hw')

        # assignment that doesn't exist at all
        with pytest.raises(AssignmentNotFoundError):
            ass_list.match('ghost assignment')

    def test_match_iter(self, ass_list):
        s_assign_exp = ['hw1', 'hw2']
        s_assign = sorted(ass_list.match_iter(s_assign='hw'))
        assert s_assign == s_assign_exp

    def test_match_iter_no_match(self, ass_list):
        s_assign = list(ass_list.match_iter(s_assign='nonexistent'))
        assert s_assign == []
