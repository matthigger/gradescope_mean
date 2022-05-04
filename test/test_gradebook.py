import pytest

from mean_scope.gradebook import *


@pytest.fixture
def gradebook():
    return Gradebook('scope.csv')


class TestGradebook:
    def test_init(self, gradebook):
        df_perc_exp = pd.read_csv('df_perc_exp.csv', index_col='email')
        df_meta_exp = pd.read_csv('df_meta_exp.csv', index_col='email')

        pd.testing.assert_frame_equal(df_meta_exp, gradebook.df_meta)
        pd.testing.assert_frame_equal(df_perc_exp, gradebook.df_perc)
        assert np.allclose([1, 2, 3, 4], gradebook.points)
        assert np.allclose([2, 3, 0, 0, 0], gradebook.df_lateday.loc[:, 'hw1'])

    def test_waive(self, gradebook):
        waive_dict = {'last0@nu.edu': 'hw1',
                      'last1@nu.edu': 'hw1, hw2'}
        gradebook.waive(waive_dict)

        assert np.isnan(gradebook.df_perc.loc['last0@nu.edu', 'hw1'])
        assert np.isnan(gradebook.df_perc.loc['last1@nu.edu', 'hw1'])
        assert np.isnan(gradebook.df_perc.loc['last1@nu.edu', 'hw2'])

    def test_substitute(self, gradebook):
        sub_dict = {'hw2': ['hw3'],
                    'hw1': ['hw1', 'hw2']}
        gradebook.substitute(sub_dict)

        assert np.allclose([1, 1, 1, 1, 1], gradebook.df_perc['hw2'])
        assert np.allclose([1, 0, 0, .5, .5], gradebook.df_perc['hw1'])

    def test_remove(self, gradebook):
        ass = 'hw1'
        gradebook.remove(ass)

        assert ass not in gradebook.df_perc.columns
        assert ass not in gradebook.df_lateday.columns
        assert ass not in gradebook.ass_list
        assert np.allclose([2, 3, 4], gradebook.points)
