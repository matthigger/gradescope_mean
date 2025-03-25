import pathlib

import pandas as pd

import gradescope_mean

# todo redundant with other test files ...
test_folder = pathlib.Path(gradescope_mean.__file__).parents[1] / 'test'


def test_predict():
    f_df_perc_exp = test_folder / 'df_perc_exp.csv'
    df = pd.read_csv(f_df_perc_exp, index_col=0)

    coef_dict, r2_score, df_out = gradescope_mean.predict(df,
                                                          ass_target='quiz1')
