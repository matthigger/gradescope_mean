import pathlib
import tempfile

import numpy as np
import pytest

import gradescope_mean
from gradescope_mean.config import *

test_folder = pathlib.Path(gradescope_mean.__file__).parents[1] / 'test'


class TestConfig:
    def test_default_config(self):
        """Default config (no categories) should process without error"""
        f_scope = test_folder / 'scope.csv'
        config = Config()
        gradebook, df_grade_full = config(f_scope)
        assert 'mean' in df_grade_full.columns
        assert 'letter' in df_grade_full.columns
        assert df_grade_full.shape[0] == 5

    def test_config_with_categories(self):
        """Config with category weights should produce per-category means"""
        f_scope = test_folder / 'scope.csv'
        config = Config(cat_weight_dict={'hw': 3, 'quiz': 1})
        gradebook, df_grade_full = config(f_scope)
        assert 'mean_hw' in df_grade_full.columns
        assert 'mean_quiz' in df_grade_full.columns

    def test_config_with_drops(self):
        f_scope = test_folder / 'scope.csv'
        config = Config(cat_weight_dict={'hw': 1, 'quiz': 0},
                        cat_drop_dict={'hw': 1})
        gradebook, df_grade_full = config(f_scope)
        np.testing.assert_allclose(
            [1, .75, .75, .8, .8], df_grade_full['mean'])

    def test_config_with_waive(self):
        f_scope = test_folder / 'scope.csv'
        config = Config(waive_dict={'last0@nu.edu': 'hw1'})
        gradebook, df_grade_full = config(f_scope)
        assert np.isnan(gradebook.df_perc.loc['last0@nu.edu', 'hw1'])

    def test_config_with_remove(self):
        f_scope = test_folder / 'scope.csv'
        config = Config(remove_list=['quiz'])
        gradebook, df_grade_full = config(f_scope)
        assert 'quiz1' not in gradebook.ass_list

    def test_from_file_default(self):
        """Loading default config.yaml should work"""
        config = Config.from_file(F_CONFIG_DEFAULT)
        f_scope = test_folder / 'scope.csv'
        gradebook, df_grade_full = config(f_scope)
        assert df_grade_full.shape[0] == 5

    def test_from_file_custom(self, tmp_path):
        """Test from_file with a custom YAML config"""
        config_content = """\
category:
  weight:
    hw: 3
    quiz: 1
  drop_low:
    hw: 1
  late_penalty: null

assignments:
  exclude_complete_thresh: null
  exclude: null
  substitute: null

waive: null

waive_late: null

email_list: null
"""
        f_config = tmp_path / 'config.yaml'
        f_config.write_text(config_content)

        config = Config.from_file(f_config)
        f_scope = test_folder / 'scope.csv'
        gradebook, df_grade_full = config(f_scope)
        assert 'mean_hw' in df_grade_full.columns
        assert 'mean_quiz' in df_grade_full.columns

    def test_from_file_with_late_waive(self, tmp_path):
        """Test that waive_late is loaded from config file"""
        config_content = """\
category:
  weight:
    hw: 1
    quiz: 0
  drop_low: null
  late_penalty:
    hw:
      penalty_per_day: 0.1
      excuse_day: 0

assignments:
  exclude_complete_thresh: null
  exclude: null
  substitute: null

waive: null

waive_late:
  last4@nu.edu: hw1

email_list: null
"""
        f_config = tmp_path / 'config.yaml'
        f_config.write_text(config_content)

        config = Config.from_file(f_config)
        assert 'last4@nu.edu' in config.late_waive_dict
