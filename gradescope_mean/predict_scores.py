import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def calculate_exam_predictions(df, hw_assignments):
    '''
    Given a clean df, predict exam score from a set of X homework assignments
    '''
    # Extract just the homework score columns
    score_cols = [f"Weighted_{hw}" for hw in hw_assignments]

    # Get the exam column
    exam_col = "Exam1"

    # Extract feature matrix (homework scores) and target vector (exam score)
    x = df[score_cols].values
    y = df[exam_col].values

    n_stud = x.shape[0]

    # Handle NaN values in homework scores: sett them to 0
    for col_idx in range(len(score_cols)):
        mask = np.isnan(x[:, col_idx])
        x[mask, col_idx] = 0

    # Handle NaN values in exam scores
    # exam_mean = np.nanmean(y)
    y[np.isnan(y)] = 0

    # Append bias column of ones to x
    x_with_bias = np.concatenate([np.ones((n_stud, 1)), x], axis=1)

    # Project y to estimates
    y_hat = x_with_bias @ np.linalg.pinv(x_with_bias) @ y

    print(
        f"Exam prediction: Predicted values: {y_hat[:5]}, Actual values: {y[:5]}")

    # Calculate z-scores (residuals)
    residuals = y - y_hat
    z = residuals / np.std(residuals)

    # Create results DataFrame
    result_df = pd.DataFrame({
        'Email': df['Email'],
        'Actual_Exam_Score': y,
        'Predicted_Exam_Score': y_hat,
        'Z_Score': z
    })

    return result_df, z


def clean_raw_csv(csv_path: str, hw_assignments: list) -> pd.DataFrame:
    '''
        This whole function can potentailly be changed
        , but it creates a score out of 100 no matter the max of the 
        assignment. 50 out of 75 -> 75%.
    '''
    df = pd.read_csv(csv_path)

    filtered_df = _cols_to_keep(df, hw_assignments).copy()
    filtered_df = filtered_df.dropna(how='all')
    filtered_df = filtered_df.dropna(axis=1, how='all')  # Discuss w/ Prof

    filtered_df['Exam1'] = np.nan
    filtered_df['Exam1 - Max Points'] = np.nan

    exam_cols = ['exam1a', 'exam1b', 'exam1c', 'exam1d']
    max_point_cols = ['exam1a - Max Points', 'exam1b - Max Points',
                      'exam1c - Max Points', 'exam1d - Max Points']  # Not sure if this exists, but maybe make it a func (generalize how)?

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


def _cols_to_keep(df, hw_assignments):
    # generalize how
    cols_to_keep = [
        'Email',
        # 'Hw1', 'Hw1 - Max Points',
        # 'Hw2', 'Hw2 - Max Points',
        # 'Hw3', 'Hw3 - Max Points',
        # 'Hw4', 'Hw4 - Max Points',
        # 'Hw5', 'Hw5 - Max Points',
        # 'hw6', 'hw6 - Max Points',
        'exam1a', 'exam1a - Max Points',
        'exam1b', 'exam1b - Max Points',
        'exam1c', 'exam1c - Max Points',
        'exam1d', 'exam1d - Max Points'
    ]

    cols_to_keep = cols_to_keep + \
        [col for hw in hw_assignments for col in [hw, f"{hw} - Max Points"]]
    return df[cols_to_keep]


hw_assignments = ['Hw1', 'Hw2', 'Hw3' , 'Hw4', 'Hw5', 'hw6']
df = clean_raw_csv(
    "file_path", hw_assignments)


results, z_scores = calculate_exam_predictions(df, hw_assignments)
# sorted_res = results.sort_values(by="Z_Score")
sorted_res = results[results['Actual_Exam_Score'] != 0].sort_values(by="Z_Score")
print(sorted_res.head())
