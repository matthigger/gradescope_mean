import pathlib

import gradescope_mean
from gradescope_mean.config import *

test_folder = pathlib.Path(gradescope_mean.__file__).parents[1] / 'test'


def test_config():
    # load default config and run on scope
    f_scope = test_folder / 'scope.csv'
    config = Config()
    config(f_scope)
