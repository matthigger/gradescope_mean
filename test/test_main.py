import pathlib
import shutil

import pytest

import gradescope_mean
from gradescope_mean.__main__ import main, parser

test_folder = pathlib.Path(gradescope_mean.__file__).parents[1] / 'test'


class TestMainCLI:
    def test_basic_run(self, tmp_path):
        """Run with default config on test CSV"""
        f_scope = tmp_path / 'scope.csv'
        shutil.copy(test_folder / 'scope.csv', f_scope)

        args = parser.parse_args([str(f_scope)])
        # first run creates config.yaml in same dir; supply --config to skip
        # the interactive prompt
        f_config = tmp_path / 'config.yaml'
        shutil.copy(
            pathlib.Path(gradescope_mean.__file__).parent / 'config.yaml',
            f_config)
        args = parser.parse_args([str(f_scope), '--config', str(f_config)])
        main(args)

        f_out = tmp_path / 'grade_full.csv'
        assert f_out.exists()

    def test_per_student(self, tmp_path):
        """--per_student should create a per_student/ folder"""
        f_scope = tmp_path / 'scope.csv'
        shutil.copy(test_folder / 'scope.csv', f_scope)
        f_config = tmp_path / 'config.yaml'
        shutil.copy(
            pathlib.Path(gradescope_mean.__file__).parent / 'config.yaml',
            f_config)

        args = parser.parse_args([str(f_scope), '--config', str(f_config),
                                  '--per_student'])
        main(args)

        per_stud_folder = tmp_path / 'per_student'
        assert per_stud_folder.exists()
        csvs = list(per_stud_folder.glob('*.csv'))
        assert len(csvs) == 5  # 5 students in test data

    def test_late_csv(self, tmp_path):
        """--late_csv should produce a late days CSV"""
        f_scope = tmp_path / 'scope.csv'
        shutil.copy(test_folder / 'scope.csv', f_scope)
        f_config = tmp_path / 'config.yaml'
        shutil.copy(
            pathlib.Path(gradescope_mean.__file__).parent / 'config.yaml',
            f_config)

        args = parser.parse_args([str(f_scope), '--config', str(f_config),
                                  '--late_csv', 'late.csv'])
        main(args)

        f_late = tmp_path / 'late.csv'
        assert f_late.exists()

    def test_plot(self, tmp_path):
        """--plot should produce an HTML histogram"""
        f_scope = tmp_path / 'scope.csv'
        shutil.copy(test_folder / 'scope.csv', f_scope)
        f_config = tmp_path / 'config.yaml'
        shutil.copy(
            pathlib.Path(gradescope_mean.__file__).parent / 'config.yaml',
            f_config)

        args = parser.parse_args([str(f_scope), '--config', str(f_config),
                                  '--plot', 'hist.html'])
        main(args)

        f_hist = tmp_path / 'hist.html'
        assert f_hist.exists()
