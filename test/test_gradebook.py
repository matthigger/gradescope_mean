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

    def test_remove0(self, gradebook):
        ass = 'hw1'
        gradebook.remove(ass)

        assert ass not in gradebook.df_perc.columns
        assert ass not in gradebook.df_lateday.columns
        assert ass not in gradebook.ass_list
        assert np.allclose([2, 3, 4], gradebook.points)

    def test_remove1(self, gradebook):
        ass = 'hw'
        gradebook.remove(ass, multi=True)

        assert np.allclose([4], gradebook.points)

    def test_average(self, gradebook):
        df_grade = gradebook.average()
        assert np.allclose([.8, .7, .7, .8, .8], df_grade['mean'])

        df_grade = gradebook.average(cat_weight_dict={'hw': 3, 'quiz': 1})
        assert np.allclose([2 / 3, .5, .5, 2 / 3, 2 / 3], df_grade['mean_hw'])
        assert np.allclose([1, 1, 1, 1, 1], df_grade['mean_quiz'])
        assert np.allclose([.75, .625, .625, .75, .75], df_grade['mean'])

        df_grade = gradebook.average(cat_weight_dict={'hw': 1, 'quiz': 0},
                                     cat_drop_dict={'hw': 1})
        assert np.allclose([1, .75, .75, .8, .8], df_grade['mean'])

    def test_average_full(self, gradebook):
        gradebook.average_full()

    def test_prune_email(self, gradebook):
        email_list = ['last0@nu.edu', 'not-in-list@nu.edu']
        with pytest.warns():
            gradebook.prune_email(email_list)

        assert gradebook.df_perc.shape[0] == 1
        assert gradebook.df_meta.shape[0] == 1
        assert gradebook.df_lateday.shape[0] == 1
