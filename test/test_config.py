from gradescope_mean.config import *


def test_config():
    # load default config and run on scope
    f_scope = 'scope.csv'
    config = Config()
    config(f_scope)
