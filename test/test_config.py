from mean_scope.config import *


def test_config():
    # load default config and run on scope
    f_scope = 'scope.csv'
    config = Config()
    config(f_scope)
