import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def calculate_assignment_z_scores(df):
    '''
        Given a clean df, predict exam Y from a set of X assignments (rn just from assignemnts and no R2)
    '''
    # Extract just the score columns
    score_cols = [col for col in df.columns if 'Max' not in col and col not in [
        'First Name', 'Last Name', 'Email'] and "Weighted" in col]  # find a better approach

    x = df[score_cols].values
    n_stud, n_ass = x.shape

    # Handle NaN values: replace NaNs with column means
    col_means = np.nanmean(x, axis=0)
    for col_idx in range(n_ass):
        mask = np.isnan(x[:, col_idx])
        x[mask, col_idx] = col_means[col_idx]

    z = np.zeros(x.shape)
    # r2_scores = np.zeros(n_ass)
    for ass_idx in range(n_ass):
        # Split to target assignment, features
        _y = x[:, ass_idx]

        # Create boolean mask
        b = np.ones(n_ass, dtype=bool)
        b[ass_idx] = False
        _x = x[:, b]

        # Append bias column of ones to _x
        _x = np.concatenate([np.ones((n_stud, 1)), _x], axis=1)

        # Project _y to estimates
        _y_hat = _x @ np.linalg.pinv(_x) @ _y

        print(
            f"Assignment {ass_idx}: Predicted values: {_y_hat[:5]}, Actual values: {_y[:5]}")

    z_score_df = pd.DataFrame(z, columns=[f"{col}_z" for col in score_cols])

    # # Create a DataFrame with the R² scores,
    # r2_df = pd.DataFrame(
    #     {f"{col}_r2": [r2_scores[i]] * n_stud for i,
    #         col in enumerate(score_cols)}
    # )

    result_df = pd.concat([df[['Email']], z_score_df], axis=1)

    return result_df, z


def clean_raw_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    filtered_df = _cols_to_keep(df).copy()
    filtered_df = filtered_df.dropna(how='all')
    filtered_df = filtered_df.dropna(axis=1, how='all')  # Discuss wq Proff
    filtered_df['Exam1'] = np.nan
    filtered_df['Exam1 - Max Points'] = np.nan
    exam_cols = ['exam1a', 'exam1b', 'exam1c', 'exam1d']
    max_point_cols = ['exam1a - Max Points', 'exam1b - Max Points',
                      'exam1c - Max Points', 'exam1d - Max Points']  # Not sure of this exists, but maybe make it a func (generalize how)?
    for i, col in enumerate(exam_cols):
        mask = filtered_df[col].notna()
        filtered_df.loc[mask, 'Exam1'] = filtered_df.loc[mask, col]
        filtered_df.loc[mask,
                        'Exam1 - Max Points'] = filtered_df.loc[mask, max_point_cols[i]]
    filtered_df = filtered_df.drop(columns=exam_cols + max_point_cols)

    for col in filtered_df.columns:
        if " - Max Points" in col:  # Identify max points columns
            # Get corresponding score column
            hw_col = col.replace(" - Max Points", "")
            if hw_col in filtered_df.columns:  # Ensure the score column exists
                filtered_df[f"Weighted_{hw_col}"] = (
                    filtered_df[hw_col] / filtered_df[col])*100

    return filtered_df


def _cols_to_keep(df):
    # generalzie how
    cols_to_keep = [
        'Email',
        'Hw1', 'Hw1 - Max Points',
        'Hw2', 'Hw2 - Max Points',
        'Hw3', 'Hw3 - Max Points',
        'Hw4', 'Hw4 - Max Points',
        'Hw5', 'Hw5 - Max Points',
        'hw6', 'hw6 - Max Points',

        'exam1a', 'exam1a - Max Points',
        'exam1b', 'exam1b - Max Points',
        'exam1c', 'exam1c - Max Points',
        'exam1d', 'exam1d - Max Points'
    ]
    return df[cols_to_keep]


df = clean_raw_csv(
    "/Users/trymkyvag/Desktop/Northeastern/Spring 25/Research Project -- Prof.Higger/gradescope_mean/real_grades/CS1800.MERGED.202530_Spring_2025_grades-2.csv")
calculate_assignment_z_scores(df)
# dfFall = pd.read_csv(
#     "/Users/trymkyvag/Desktop/Northeastern/Spring 25/Research Project -- Prof.Higger/gradescope_mean/real_grades/CS1800.MERGED.202510_Fall_2024_grades.csv")
