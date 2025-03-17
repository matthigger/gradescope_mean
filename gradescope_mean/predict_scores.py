import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


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

    r2 = r2_score(y, y_hat)  # hmmm

    # Calculate z-scores (residuals)
    residuals = y - y_hat
    z = residuals / np.std(residuals)

    # Create results DataFrame
    result_df = pd.DataFrame({
        'Email': df['Email'],
        'Actual_Exam_Score': y,
        'Predicted_Exam_Score': y_hat,
        'Z_Score': z,
        'R2_Score': [r2] * n_stud
    })

    return result_df, z


def calculate_x_predictions(df, hw_assignments):
    '''
    For every assignment x, predict its score based on all others via linear regression.
    Express each student's residual as a z score (divide by regression error std dev).
    Identify largest magnitude z scores (biggest surprise performers on each assignment).
    '''
    # Extract homework score columns and exam column
    weighted_hw_cols = [f"Weighted_{hw}" for hw in hw_assignments]
    all_cols = weighted_hw_cols + ["Exam1"]
    assignment_names = hw_assignments + ["Exam1"]

    # Filter to only include students with valid exam scores
    valid_students = df["Exam1"].notna()
    valid_df = df[valid_students].copy()
    emails = valid_df['Email'].values

    # Create matrix of all scores (homework and exam)
    x = np.zeros((valid_df.shape[0], len(all_cols)))

    # Fill matrix with values, replacing NaN with 0
    for col_idx, col in enumerate(all_cols):
        values = valid_df[col].values
        values[np.isnan(values)] = 0
        x[:, col_idx] = values

    # Get dimensions
    n_stud, n_ass = x.shape

    # Initialize z-scores and R2 values arrays
    z = np.zeros(x.shape)
    r2_values = np.zeros(n_ass)

    for ass_idx in range(n_ass):

        # split to target assignment & features
        _y = x[:, ass_idx]
        b = np.ones(n_ass, dtype=bool)
        b[ass_idx] = False
        _x = x[:, b]

        # append bias column of ones to x (allows nonzero intercept)
        _x = np.concatenate([np.ones((n_stud, 1)), _x], axis=1)

        # project _y to estimates
        _y_hat = _x @ np.linalg.pinv(_x) @ _y

        # compute z score
        err = _y - _y_hat
        z[:, ass_idx] = err / np.std(err)

        # calculate R2 value
        r2_values[ass_idx] = r2_score(_y, _y_hat)

    all_results = []

    for ass_idx in range(n_ass):
        for stud_idx in range(n_stud):
            all_results.append({
                'Email': emails[stud_idx],
                'Assignment': assignment_names[ass_idx],
                'Z_Score': z[stud_idx, ass_idx],
                'R2': r2_values[ass_idx]
            })

    results_df = pd.DataFrame(all_results)

    # Find top outliers for each assignment
    print("Top outliers for each assignment (predicted from all others):")
    for ass_name in assignment_names:
        ass_results = results_df[results_df['Assignment'] == ass_name].copy()
        ass_results['abs_z'] = ass_results['Z_Score'].abs()
        top_outliers = ass_results.sort_values(
            'abs_z', ascending=False).head(3)

        r2 = top_outliers['R2'].iloc[0]
        print(f"\n{ass_name} (R² = {r2:.2f}):")

        for _, row in top_outliers.iterrows():
            direction = "+" if row['Z_Score'] > 0 else "-"
            print(
                f"  {direction}{abs(row['Z_Score']):.1f} std dev: {row['Email']}")

    # Identify students who consistently over/underperform
    print("\nConsistency analysis (students who tend to over/underperform):")
    student_means = results_df.groupby('Email')['Z_Score'].mean().sort_values()
    student_stds = results_df.groupby('Email')['Z_Score'].std()

    # Consistent underperformers (negative mean z-score)
    print("\nConsistent underperformers:")
    for email, mean_z in student_means.head(3).items():
        std_z = student_stds[email]
        print(f"  {email}: mean z-score = {mean_z:.2f}, std = {std_z:.2f}")

    # Consistent overperformers (positive mean z-score)
    print("\nConsistent overperformers:")
    for email, mean_z in student_means.tail(3).items():
        std_z = student_stds[email]
        print(f"  {email}: mean z-score = {mean_z:.2f}, std = {std_z:.2f}")

    # Exam vs homework performance patterns
    print("\nExam vs homework performance patterns:")
    for _, student in valid_df.iterrows():
        email = student['Email']
        hw_zs = results_df[(results_df['Email'] == email) &
                           (results_df['Assignment'] != 'Exam1')]['Z_Score'].mean()
        exam_z = results_df[(results_df['Email'] == email) &
                            (results_df['Assignment'] == 'Exam1')]['Z_Score'].iloc[0]

        # Look for large discrepancies between homework and exam performance
        if abs(hw_zs - exam_z) > 1.5:
            pattern = "performs better on exam than homework" if exam_z > hw_zs else "performs better on homework than exam"
            print(
                f"  {email}: {pattern} (hw avg z = {hw_zs:.2f}, exam z = {exam_z:.2f})")

    return results_df, z, r2_values


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


hw_assignments = ['Hw1', 'Hw2', 'Hw3', 'Hw4', 'Hw5', 'hw6']
df = clean_raw_csv(
    "/Users/trymkyvag/Desktop/Northeastern/Spring 25/Research Project -- Prof.Higger/gradescope_mean/real_grades/CS1800.MERGED.202530_Spring_2025_grades-2.csv", hw_assignments)


results, z_scores = calculate_exam_predictions(df, hw_assignments)
sorted_res = results[results['Actual_Exam_Score']
                     != 0].sort_values(by="Z_Score")

# sorted_res = results.sort_values(by="Z_Score")
# sorted_res = results[results['Actual_Exam_Score']
#                      != 0].sort_values(by="Z_Score")
print(sorted_res.head())


df = pd.DataFrame(sorted_res)
z_min, z_max = -5, 4  
filtered_df = df[(df['Z_Score'] >= z_min) & (df['Z_Score'] <= z_max)]
bin_size = 0.5  # Adjust bin size as needed
filtered_df['Z_Bin'] = (filtered_df['Z_Score'] // bin_size) * bin_size
bin_groups = filtered_df.groupby('Z_Bin')['Email'].apply(list).reset_index()

fig = go.Figure()
fig.add_trace(go.Histogram(
    x=filtered_df['Z_Score'],
    xbins=dict(size=bin_size),
    marker=dict(color='blue', opacity=0.7),
    hoverinfo='x+y',
    name='Z-Score Distribution'
))

hover_texts = []
for _, row in bin_groups.iterrows():
    z_bin = row['Z_Bin']
    email_list = '<br>'.join(row['Email'])
    hover_text = (
        f"<b>Z-Score Range:</b> {z_bin:.2f} - {z_bin + bin_size:.2f}<br>"
        f"<b>Students:</b><br>"
        f"<b>{email_list}</b>"
    )
    hover_texts.append((z_bin, hover_text))

fig.update_traces(
    hoverinfo='x+y+text',
    text=[hover_texts[i][1] if i < len(hover_texts) else '' for i in range(len(filtered_df['Z_Score']))],
    textposition='none'
)

fig.update_layout(
    title='Histogram of Students within Z-Score Range',
    xaxis_title='Z Score',
    yaxis_title='Count',
    hovermode='x unified'
)
fig.write_html("histogram.html")

print("Histogram saved as histogram.html")