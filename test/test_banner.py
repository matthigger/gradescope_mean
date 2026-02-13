import pathlib
import shutil

import pandas as pd
import pytest

import gradescope_mean
from gradescope_mean.banner.__main__ import main as banner_main, parser as banner_parser
from gradescope_mean.config import Config

test_folder = pathlib.Path(gradescope_mean.__file__).parents[1] / 'test'


@pytest.fixture
def grade_full_csv(tmp_path):
    """Create a grade_full.csv from test data"""
    config = Config()
    _, df_grade_full = config(f_scope=test_folder / 'scope.csv')
    f = tmp_path / 'grade_full.csv'
    df_grade_full.to_csv(f)
    return str(f)


class TestBanner:
    def test_basic_banner_export(self, grade_full_csv, tmp_path):
        args = banner_parser.parse_args([
            grade_full_csv,
            '202310',
            '-c', '12345',
        ])
        banner_main(args)

        # output should be an xlsx file
        xlsx_files = list(tmp_path.glob('*banner*.xlsx'))
        assert len(xlsx_files) == 1

        df = pd.read_excel(xlsx_files[0])
        assert 'Term Code' in df.columns
        assert 'CRN0' in df.columns
        assert 'Student ID' in df.columns
        # Student IDs should have no 'S' prefix and be zero-padded
        for sid in df['Student ID']:
            sid_str = str(sid)
            assert 'S' not in sid_str
            assert sid_str.isdigit()

    def test_multiple_crns(self, grade_full_csv, tmp_path):
        args = banner_parser.parse_args([
            grade_full_csv,
            '202310',
            '-c', '11111',
            '-c', '22222',
        ])
        banner_main(args)

        xlsx_files = list(tmp_path.glob('*banner*.xlsx'))
        assert len(xlsx_files) == 1

        df = pd.read_excel(xlsx_files[0])
        assert 'CRN0' in df.columns
        assert 'CRN1' in df.columns
