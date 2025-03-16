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


    return df


