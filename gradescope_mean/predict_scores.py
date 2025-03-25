import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
from typing import List, Tuple, Optional

import assign_list as al


def calculate_predictions(df: pd.DataFrame,
                          target_assignment: str,
                          predictor_assignments: Optional[List[str]] = None,
                          target_category_name: str = "Target",
                          predictor_category_name: str = "Predictors") -> Tuple[pd.DataFrame, np.ndarray]:
    '''
    General prediction function: predict scores for target assignments from predictor assignments

    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe containing assignment scores
    target_assignment : str
        Assignment to predict (e.g., "Exam1" or "Exam2")
    predictor_assignments : Optional[List[str]]
        List of assignments to use as predictors. If None, uses all assignments except targets.
    target_category_name : str
        Name to use when describing the target category (e.g., "Exam", "Final Project")
    predictor_category_name : str
        Name to use when describing the predictor category (e.g., "Homework", "Assignments")

    Returns:
    --------
    result_df : pd.DataFrame
        DataFrame with prediction results
    z_scores : np.ndarray
        Z-scores for all predictions
    '''

    # Extract emails for output
    emails = df['Email']

    # Predictor assignments if not provided
    if predictor_assignments is None:
        weighted_cols = [
            col for col in df.columns if col.startswith('Weighted_')]
        predictor_assignments = [col.replace('Weighted_', '') for col in weighted_cols
                                 if col.replace('Weighted_', '') != target_assignment]

    target_col = f"Weighted_{target_assignment}"
    predictor_cols = [f"Weighted_{hw}" for hw in predictor_assignments]

    # Keep only relevant columns and drop rows with missing target values
    data = df[['Email', target_col] +
              predictor_cols].dropna(subset=[target_col])

    x = data[predictor_cols].fillna(0).values
    y = data[target_col].values

    # Append bias column of ones to x
    x_with_bias = np.concatenate([np.ones((x.shape[0], 1)), x], axis=1)

    # Project y to estimates using pseudoinverse
    y_hat = x_with_bias @ np.linalg.pinv(x_with_bias) @ y
    r2 = r2_score(y, y_hat)
    residuals = y - y_hat
    z = residuals / np.std(residuals)

    # Create result DataFrame
    result_df = pd.DataFrame({
        'Email': data['Email'],
        'Target': target_assignment,
        'Actual_Score': y,
        'Predicted_Score': y_hat,
        'Z_Score': z,
        'R2_Score': r2
    })

    return result_df, z


# def detect_assignment_categories(df: pd.DataFrame) -> Dict[str, List[str]]:
#     """
#     Automatically detect homework and exam assignments from column names.

#     Parameters:
#     -----------
#     df : pd.DataFrame
#         Dataframe containing assignment scores

#     Returns:
#     --------
#     Dict[str, List[str]]
#         Dictionary with keys 'homeworks' and 'exams' containing lists of assignment names
#     """
#     # Get columns that have been weighted (to 100)
#     weighted_cols = [col for col in df.columns if col.startswith('Weighted_')]
#     assignment_names = [col.replace('Weighted_', '') for col in weighted_cols]

#     # Categorize by exam and hw
#     exams = [name for name in assignment_names if 'exam' in name.lower()]
#     homeworks = [name for name in assignment_names if 'hw' in name.lower(
#     ) or 'homework' in name.lower()]

#     # Idk if we are going to have others
#     other = [
#         name for name in assignment_names if name not in exams and name not in homeworks]

#     return {
#         'exams': exams,
#         'homeworks': homeworks,
#         'other': other
#     }


# def clean_raw_csv(csv_path: str, hw_assignments: Optional[List[str]] = None) -> pd.DataFrame:
#     '''
#     Clean and prepare raw CSV data for analysis.

#     Parameters:
#     -----------
#     csv_path : str
#         Path to the CSV file
#     hw_assignments : Optional[List[str]]
#         List of homework assignments to include. If None, will try to detect automatically.

#     Returns:
#     --------
#     pd.DataFrame
#         Cleaned dataframe with weighted scores
#     '''
#     df = pd.read_csv(csv_path)

#     # If hw_assignments not provided, try to detect from column names
#     if hw_assignments is None:
#         possible_hw_cols = [
#             col for col in df.columns if 'hw' in col.lower() and ' - Max Points' not in col]
#         hw_assignments = [
#             col for col in possible_hw_cols if f"{col} - Max Points" in df.columns]

#     # Detect exam columns
#     exam_cols = [col for col in df.columns if 'exam' in col.lower()
#                  and ' - Max Points' not in col]
#     exam_cols = [
#         col for col in exam_cols if f"{col} - Max Points" in df.columns]

#     # Get all assignments to keep
#     all_assignments = hw_assignments + exam_cols

#     # Columns to keep
#     cols_to_keep = ['Email'] + [col for assignment in all_assignments
#                                 for col in [assignment, f"{assignment} - Max Points"]]

#     # Filter dataframe
#     filtered_df = df[cols_to_keep].copy()
#     filtered_df = filtered_df.dropna(how='all')
#     filtered_df = filtered_df.dropna(axis=1, how='all')

#     # Calculate weighted scores (as percentage of max points)
#     for col in filtered_df.columns:
#         if " - Max Points" in col:  # Identify max points columns
#             # Get corresponding score column
#             assignment_col = col.replace(" - Max Points", "")
#             if assignment_col in filtered_df.columns:  # Ensure the score column exists
#                 filtered_df[f"Weighted_{assignment_col}"] = (
#                     filtered_df[assignment_col] / filtered_df[col]) * 100

    # return filtered_df


def plot_z_score_histogram(df: pd.DataFrame, z_min: float = -5, z_max: float = 4,
                           bin_size: float = 0.5, output_file: str = "histogram.html",
                           title: str = "Histogram of Student Performance Residuals"):
    """
    Create and save a histogram of Z-scores with hover information.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing Z-scores and student emails
    z_min, z_max : float
        Min and max Z-score to include in histogram
    bin_size : float
        Size of histogram bins
    output_file : str
        Path to save HTML output file
    title : str
        Title for the histogram
    """
    # Filter data to remove extreme outliers
    filtered_df = df[(df['Z_Score'] >= z_min) & (df['Z_Score'] <= z_max)]

    # Bin Z-scores for hover text grouping
    filtered_df = filtered_df.copy()
    filtered_df.loc[:, 'Z_Bin'] = (
        filtered_df['Z_Score'] // bin_size) * bin_size

    bin_groups = filtered_df.groupby(['Z_Bin'])[
        'Email'].apply(list).reset_index()

    # Create figure
    fig = go.Figure()

    # Add histogram trace
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
        text=[hover_texts[i][1] if i < len(
            hover_texts) else '' for i in range(len(filtered_df['Z_Score']))],
        textposition='none'
    )

    fig.update_layout(
        title=title,
        xaxis_title='Z Score (Standard Deviations from Predicted)',
        yaxis_title='Count',
        hovermode='x unified'
    )

    # Save figure / do we wanna change to where?
    fig.write_html(output_file)

    return fig


def run_analysis(csv_path: str,
                 target_assignment: Optional[str] = None,
                 predictor_assignments: Optional[List[str]] = None,
                 target_category_name: Optional[str] = None,
                 predictor_category_name: Optional[str] = None,
                 auto_detect: bool = True,
                 file_path: str = "Histogram.html"):
    """
    Run the full analysis pipeline with clear reporting.

    Parameters:
    -----------
    csv_path : str
        Path to the CSV file
    target_assignment : Optional[str]]
        List of assignments to predict. If None and auto_detect=True, will use detected exams.
    predictor_assignments : Optional[List[str]]
        List of assignments to use as predictors. If None and auto_detect=True, will use detected homeworks.
    target_category_name : Optional[str]
        Name for the target category. Defaults to "Exam" if auto-detecting exams.
    predictor_category_name : Optional[str]
        Name for the predictor category. Defaults to "Homework" if auto-detecting homeworks.
    auto_detect : bool
        Whether to automatically detect assignment categories if not specified
    """
    df = pd.read_csv(csv_path)

    alist = al.AssignmentList(df.columns)
    # Detect categories if using auto-detection
    # if auto_detect:
    #     categories = detect_assignment_categories(df)

    # Use detected categories if not specified
    if target_assignment is None and auto_detect:
        target_assignment = alist.match(target_assignment)
        if not target_category_name:
            target_category_name = "Exam"

    if predictor_assignments is None and auto_detect:
        # predictor_assignments = categories['homeworks']
        # TODO: use assinList to get hw
        if not predictor_category_name:
            predictor_category_name = "Homework"

    if not target_assignment:
        raise ValueError("No target assignments specified or detected")

    # Set default category names if not provided
    if not target_category_name:
        target_category_name = "Target"
    if not predictor_category_name:
        predictor_category_name = "Predictor"

    # Run prediction
    results, z_scores = calculate_predictions(
        df,
        target_assignment,
        predictor_assignments,
        target_category_name,
        predictor_category_name
    )

    # Plot histogram
    if not results.empty:
        title = f"Prediction Residuals: {target_category_name} from {predictor_category_name}"
        plot_z_score_histogram(results, title=title, output_file=file_path)

    return df, results, z_scores


if __name__ == "__main__":
    csv_path = "path"

    # Option 1: Auto-detect assignments and categories
    # df, results, z_scores = run_analysis(csv_path, auto_detect=True)
    # print("s")
    # Option 2: Explicitly specify everything
    df, results, z_scores = run_analysis(
        csv_path,
        target_assignment="exam1a",  # , "Exam2"],
        predictor_assignments=["hw1", "hw2", "hw3", "hw4"],
        target_category_name="Exams",
        predictor_category_name="Homework Assignments",
        auto_detect=False
    )
    print("s")
