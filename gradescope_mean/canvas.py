from datetime import datetime

import pandas as pd


def canvas_merge(f_canvas, df_grade_full, meta_col_list):
    # we discard all canvas grades
    N_COL_CANVAS_KEEP = 5

    # load df_canvas & merge
    df_canvas = pd.read_csv(f_canvas)
    df_canvas = df_canvas.iloc[:, :N_COL_CANVAS_KEEP]

    # merge
    df_canvas.set_index('SIS User ID', inplace=True)
    df_grade_full.set_index('sid', inplace=True)
    df_canvas_out = df_canvas.merge(df_grade_full,
                                    left_index=True,
                                    right_index=True,
                                    how='left')

    def print_missing(df, idx_missing, msg, n_cols=3):
        if not idx_missing:
            print('<no students>')
        print(msg)
        for idx in idx_missing:
            print(df.loc[idx, :].iloc[:n_cols].to_dict())

    # find and print canvas students not in gradescope
    idx_missing = set(df_canvas.index) - set(df_grade_full.index)
    print_missing(df=df_canvas,
                  idx_missing=idx_missing,
                  msg='students in canvas, not in gradescope:')

    idx_missing = set(df_grade_full.index) - set(df_canvas.index)
    print_missing(df=df_grade_full,
                  idx_missing=idx_missing,
                  msg='students in gradescope, not in canvas:')

    # strip out our metadata
    df_canvas_out.index.name = 'sid'
    df_canvas_out.reset_index(inplace=True)
    for col in meta_col_list:
        del df_canvas_out[col]

    # output csv
    timestamp = datetime.now().strftime('%b%d_%H%M')
    f_canvas_out = f_canvas.replace('.csv', f'{timestamp}.csv')
    df_canvas_out.to_csv(f_canvas_out, index=False)
