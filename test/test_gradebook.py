import pytest

from mean_scope.gradebook import *


@pytest.fixture
def gradebook():
    return Gradebook('scope.csv')


class TestGradebook:
    def test_init(self, gradebook):
        df_exp = pd.read_csv('df_exp.csv', index_col='email')

        pd.testing.assert_frame_equal(df_exp, gradebook.df)
        assert np.allclose([1, 2, 3, 4], gradebook.points)
        assert np.allclose([2, 3, 0, 0, 0], gradebook.df_lateday.loc[:, 'hw1'])

    def test_waive(self, gradebook):
        waive_dict = {'last0@nu.edu': 'hw1',
                      'last1@nu.edu': 'hw1, hw2'}
        gradebook.waive(waive_dict)

        assert np.isnan(gradebook.df.loc['last0@nu.edu', 'hw1'])
        assert np.isnan(gradebook.df.loc['last1@nu.edu', 'hw1'])
        assert np.isnan(gradebook.df.loc['last1@nu.edu', 'hw2'])

    def test_substitute(self, gradebook):
        sub_dict = {'hw2': ['hw3'],
                    'hw1': ['hw1', 'hw2']}
        gradebook.substitute(sub_dict)

        assert np.allclose([1, 1, 1, 1, 1], gradebook.df['hw2'])
        assert np.allclose([1, 0, 0, .5, .5], gradebook.df['hw1'])
