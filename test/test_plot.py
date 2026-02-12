import pathlib

import numpy as np
import pytest

import gradescope_mean
from gradescope_mean.config import Config, F_CONFIG_DEFAULT
from gradescope_mean.gradebook import Gradebook
from gradescope_mean.plot import plot_hist, plot_pca

test_folder = pathlib.Path(gradescope_mean.__file__).parents[1] / 'test'


@pytest.fixture
def grade_data():
    """Return (gradebook, df_grade_full, cat_weight_dict) for test data"""
    cat_weight_dict = {'hw': 3, 'quiz': 1}
    config = Config(cat_weight_dict=cat_weight_dict)
    gradebook, df_grade_full = config(f_scope=test_folder / 'scope.csv')
    return gradebook, df_grade_full, cat_weight_dict


class TestPlot:
    def test_plot_hist(self, grade_data):
        gradebook, df_grade_full, cat_weight_dict = grade_data
        fig = plot_hist(df_grade_full=df_grade_full,
                        cat_weight_dict=cat_weight_dict)
        # should return a plotly figure with traces
        assert fig is not None
        assert len(fig.data) > 0

    def test_plot_hist_no_categories(self):
        config = Config()
        gradebook, df_grade_full = config(f_scope=test_folder / 'scope.csv')
        fig = plot_hist(df_grade_full=df_grade_full, cat_weight_dict=None)
        assert fig is not None

    def test_plot_pca(self):
        """PCA needs enough variance; use a bigger synthetic dataset"""
        import pandas as pd
        np.random.seed(42)
        n = 20
        data = {
            'firstname': [f'first{i}' for i in range(n)],
            'lastname': [f'last{i}' for i in range(n)],
            'sid': list(range(n)),
            'section_name': ['sec'] * n,
            'mean': np.random.uniform(.5, 1, n),
            'mean_hw': np.random.uniform(.4, 1, n),
            'mean_quiz': np.random.uniform(.6, 1, n),
            'letter': ['B'] * n,
            'hw1': np.random.uniform(0, 1, n),
            'hw2': np.random.uniform(0, 1, n),
            'hw3': np.random.uniform(0, 1, n),
            'quiz1': np.random.uniform(0, 1, n),
        }
        df = pd.DataFrame(data)
        df.index.name = 'email'
        cat_weight_dict = {'hw': 3, 'quiz': 1}
        point_dict = {'hw1': 1.0, 'hw2': 2.0, 'hw3': 3.0, 'quiz1': 4.0}
        fig = plot_pca(df_grade_full=df,
                       cat_weight_dict=cat_weight_dict,
                       point_dict=point_dict)
        assert fig is not None
        assert len(fig.data) > 0
