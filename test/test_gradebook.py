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
