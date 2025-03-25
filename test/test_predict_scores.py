import pathlib

import numpy as np
import pandas as pd

import gradescope_mean

# todo redundant with other test files ...
test_folder = pathlib.Path(gradescope_mean.__file__).parents[1] / 'test'


def test_predict():
    df = pd.read_csv(test_folder / 'df_test_predict.csv', index_col=0)

    coef_dict, r2_score, df_out = gradescope_mean.predict(df,
                                                          ass_target='quiz1')

    # load expected values & assert
    df_out_exp = pd.read_csv(test_folder / 'df_test_predict_out.csv',
                             index_col=0)
    coef_dict_exp = {'bias': 0.0566666666666666,
                     'hw1': 0.9600000000000002,
                     'hw2': 0.1333333333333322,
                     'hw3': 0.0566666666666666}
    r2_score_exp = 0.9955776672194583
    pd.testing.assert_frame_equal(df_out, df_out_exp)
    assert coef_dict == coef_dict_exp
    assert np.isclose(r2_score, r2_score_exp)

    # test: restrict predictors
    coef_dict, r2_score, df_out = gradescope_mean.predict(df,
                                                          ass_target='quiz1',
                                                          ass_predict='hw1')
    assert set(coef_dict.keys()) == {'bias', 'hw1'}

    # test: restrict columns (exclude last1@nu.edu whose hw3 is missing)
    coef_dict, r2_score, df_out = gradescope_mean.predict(df, ass_target='hw3')
    assert 'last1@nu.edu' not in df_out.index
