import pytest

from gradescope_mean.gradebook import *


@pytest.fixture
def gradebook():
    return Gradebook('scope.csv')


class TestGradebook:
    def test_init(self, gradebook):
        df_perc_exp = pd.read_csv('df_perc_exp.csv', index_col='email')
        df_meta_exp = pd.read_csv('df_meta_exp.csv', index_col='email',
                                  converters={'sid': str, 'crn': str})

        pd.testing.assert_frame_equal(df_meta_exp, gradebook.df_meta,
                                      check_dtype=False)
        pd.testing.assert_frame_equal(df_perc_exp, gradebook.df_perc)
        np.testing.assert_allclose([1, 2, 3, 4], gradebook.points)
        np.testing.assert_allclose([0, 1, 2, 3, 4],
                                   gradebook.df_lateday.loc[:, 'hw1'])

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

        np.testing.assert_allclose([1, 1, 1, 1, 1], gradebook.df_perc['hw2'])
        np.testing.assert_allclose([1, 0, 0, .5, .5], gradebook.df_perc['hw1'])

    def test_remove0(self, gradebook):
        ass = 'hw1'
        gradebook.remove(ass)

        assert ass not in gradebook.df_perc.columns
        assert ass not in gradebook.df_lateday.columns
        assert ass not in gradebook.ass_list
        np.testing.assert_allclose([2, 3, 4], gradebook.points)

    def test_remove1(self, gradebook):
        ass = 'hw'
        gradebook.remove(ass, multi=True)

        np.testing.assert_allclose([4], gradebook.points)

    def test_get_late_penalty(self, gradebook):
        # remember: students use [0, 1, 2, 3, 4] late days on 'hw1'
        s_penalty = gradebook.get_late_penalty(cat='hw1', penalty_per_day=.1,
                                               excuse_day=0)
        penalty_exp = np.array([0, -.1, -.2, -.3, -.4])
        np.testing.assert_allclose(penalty_exp, s_penalty)

        # with 3 assignments in category, mean penalty goes down to 1/3
        s_penalty = gradebook.get_late_penalty(cat='hw', penalty_per_day=.1,
                                               excuse_day=0)
        np.testing.assert_allclose(penalty_exp / 3, s_penalty)

        # with 1 excused late date for all students, penalties drop a notch
        s_penalty = gradebook.get_late_penalty(cat='hw1', penalty_per_day=.1,
                                               excuse_day=1)
        penalty_exp = np.array([0, 0, -.1, -.2, -.3])
        np.testing.assert_allclose(penalty_exp, s_penalty)

        # excusing different number of assignments per student
        s_penalty = \
            gradebook.get_late_penalty(cat='hw1', penalty_per_day=.1,
                                       excuse_day=1,
                                       excuse_day_adjust={'last4@nu.edu': 4,
                                                          'last3@nu.edu': 0})
        penalty_exp = np.array([0, 0, -.1, -.3, 0])
        np.testing.assert_allclose(penalty_exp, s_penalty)

    def test_average(self, gradebook):
        df_grade = gradebook.average()
        np.testing.assert_allclose([.8, .7, .7, .8, .8], df_grade['mean'])
        assert ['B-', 'C-', 'C-', 'B-', 'B-'] == df_grade['letter'].tolist()

        df_grade = gradebook.average(cat_weight_dict={'hw': 3, 'quiz': 1})
        np.testing.assert_allclose([2 / 3, .5, .5, 2 / 3, 2 / 3],
                                   df_grade['mean_hw'])
        np.testing.assert_allclose([1, 1, 1, 1, 1], df_grade['mean_quiz'])
        np.testing.assert_allclose([.75, .625, .625, .75, .75],
                                   df_grade['mean'])

        df_grade = gradebook.average(cat_weight_dict={'hw': 1, 'quiz': 0},
                                     cat_drop_dict={'hw': 1})
        np.testing.assert_allclose([1, .75, .75, .8, .8], df_grade['mean'])

        kwargs = {'penalty_per_day': 1}
        df_grade = gradebook.average(cat_weight_dict={'hw': 1, 'quiz': 0},
                                     cat_late_dict={'hw': kwargs})
        np.testing.assert_allclose([2 / 3, 1 / 6, 0, 0, 0],
                                   df_grade['mean_hw'])

        with pytest.warns(UserWarning):
            # warns other assignments not included
            gradebook.average(cat_weight_dict={'hw1': 1})

        with pytest.warns(UserWarning):
            # warns hw1 in two categories
            gradebook.average(cat_weight_dict={'hw': 1, 'hw1': 1, 'quiz': 1})

    def test_average_full(self, gradebook):
        gradebook.average_full()

    def test_prune_email(self, gradebook):
        email_list = ['last0@nu.edu', 'not-in-list@nu.edu']
        with pytest.warns():
            gradebook.prune_email(email_list)

        assert gradebook.df_perc.shape[0] == 1
        assert gradebook.df_meta.shape[0] == 1
        assert gradebook.df_lateday.shape[0] == 1

        email_list = ['last0@gmail.com']
        gradebook.prune_email(email_list, ignore_suffix=True)
        assert gradebook.df_perc.shape[0] == 1
