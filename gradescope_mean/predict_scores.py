import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from typing import List, Dict, Tuple, Optional


def calculate_predictions(df: pd.DataFrame,
                          target_assignments: List[str],
                          predictor_assignments: Optional[List[str]] = None,
                          target_category_name: str = "Target",
                          predictor_category_name: str = "Predictors") -> Tuple[pd.DataFrame, np.ndarray]:
    '''
    General prediction function: predict scores for target assignments from predictor assignments

    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe containing assignment scores
    target_assignments : List[str]
        List of assignments to predict (e.g., ["Exam1", "Exam2"])
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
    print(f"\n===== Estimating {target_category_name} ({', '.join(target_assignments)}) " +
          f"from {predictor_category_name} ({', '.join(predictor_assignments or [])}) =====")

    # Extract emails for output
    emails = df['Email'].values

    # If predictor_assignments is None, use all assignments except targets
    if predictor_assignments is None:
        weighted_cols = [
            col for col in df.columns if col.startswith('Weighted_')]
        predictor_assignments = [col.replace('Weighted_', '') for col in weighted_cols
                                 if col.replace('Weighted_', '') not in target_assignments]
        print(
            f"No predictors specified, using all available: {predictor_assignments}")

    target_cols = [f"Weighted_{hw}" for hw in target_assignments]
    predictor_cols = [f"Weighted_{hw}" for hw in predictor_assignments]

    # Extract feature matrix and target vector 
    x = df[predictor_cols].values

    # Handle NaN values in predictor scores: set them to 0 since we mask them
    for col_idx in range(len(predictor_cols)):
        mask = np.isnan(x[:, col_idx])
        if np.any(mask):
            print(
                f"Note: {sum(mask)} missing values in {predictor_cols[col_idx]} set to 0")
        x[mask, col_idx] = 0

    # Initialize results storage
    all_results = []
    z_scores_dict = {}

    # For each target assignment, perform prediction
    for target_idx, target_col in enumerate(target_cols):
        y = df[target_col].values

        missing_mask = np.isnan(y)
        if np.any(missing_mask):
            print(
                f"Skipping {sum(missing_mask)} students with missing {target_col} scores")

        # Filter to only students with valid target scores (they took exam)
        valid_indices = ~missing_mask
        valid_emails = emails[valid_indices]
        valid_x = x[valid_indices]
        valid_y = y[valid_indices]

        if len(valid_y) == 0:
            print(f"No valid scores for {target_col}, skipping")
            continue

        # Append bias column of ones to x
        x_with_bias = np.concatenate(
            [np.ones((valid_x.shape[0], 1)), valid_x], axis=1)

        # Project y to estimates
        y_hat = x_with_bias @ np.linalg.pinv(x_with_bias) @ valid_y

        # Calculate R2 score
        r2 = r2_score(valid_y, y_hat)

        # Calculate z-scores
        residuals = valid_y - y_hat
        z = residuals / np.std(residuals)

        z_scores_dict[target_assignments[target_idx]] = {
            'emails': valid_emails,
            'z_scores': z,
            'r2': r2
        }

        print(
            f"\nPrediction for {target_assignments[target_idx]} (R² = {r2:.2f}):")
        print(
            f"  Sample predictions: Actual: {valid_y[:3]} | Predicted: {y_hat[:3]}")

        z_abs = np.abs(z)
        sorted_indices = np.argsort(z_abs)[::-1]

        print(f"\nTop outliers for {target_assignments[target_idx]}:")
        for i in range(min(3, len(sorted_indices))):
            idx = sorted_indices[i]
            direction = "+" if z[idx] > 0 else "-"
            print(
                f"  {direction}{abs(z[idx]):.1f} std dev: {valid_emails[idx]}")

        for i in range(len(valid_emails)):
            all_results.append({
                'Email': valid_emails[i],
                'Target': target_assignments[target_idx],
                'Actual_Score': valid_y[i],
                'Predicted_Score': y_hat[i],
                'Z_Score': z[i],
                'R2_Score': r2
            })

    result_df = pd.DataFrame(all_results)

    return result_df, z_scores_dict


def detect_assignment_categories(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Automatically detect homework and exam assignments from column names.

    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe containing assignment scores

    Returns:
    --------
    Dict[str, List[str]]
        Dictionary with keys 'homeworks' and 'exams' containing lists of assignment names
    """
    # Get columns that have been weighted (to 100)
    weighted_cols = [col for col in df.columns if col.startswith('Weighted_')]
    assignment_names = [col.replace('Weighted_', '') for col in weighted_cols]

    # Categorize by exam and hw
    exams = [name for name in assignment_names if 'exam' in name.lower()]
    homeworks = [name for name in assignment_names if 'hw' in name.lower(
    ) or 'homework' in name.lower()]

    # Idk if we are going to have others
    other = [
        name for name in assignment_names if name not in exams and name not in homeworks]

    return {
        'exams': exams,
        'homeworks': homeworks,
        'other': other
    }


def clean_raw_csv(csv_path: str, hw_assignments: Optional[List[str]] = None) -> pd.DataFrame:
    '''
    Clean and prepare raw CSV data for analysis.

    Parameters:
    -----------
    csv_path : str
        Path to the CSV file
    hw_assignments : Optional[List[str]]
        List of homework assignments to include. If None, will try to detect automatically.

    Returns:
    --------
    pd.DataFrame
        Cleaned dataframe with weighted scores
    '''
    df = pd.read_csv(csv_path)

    # If hw_assignments not provided, try to detect from column names
    if hw_assignments is None:
        possible_hw_cols = [
            col for col in df.columns if 'hw' in col.lower() and ' - Max Points' not in col]
        hw_assignments = [
            col for col in possible_hw_cols if f"{col} - Max Points" in df.columns]
        print(f"Auto-detected homework assignments: {hw_assignments}")

    # Detect exam columns
    exam_cols = [col for col in df.columns if 'exam' in col.lower()
                 and ' - Max Points' not in col]
    exam_cols = [
        col for col in exam_cols if f"{col} - Max Points" in df.columns]
    print(f"Auto-detected exam assignments: {exam_cols}")

    # Get all assignments to keep
    all_assignments = hw_assignments + exam_cols

    # Columns to keep
    cols_to_keep = ['Email'] + [col for assignment in all_assignments
                                for col in [assignment, f"{assignment} - Max Points"]]

    # Filter dataframe
    filtered_df = df[cols_to_keep].copy()
    filtered_df = filtered_df.dropna(how='all')
    filtered_df = filtered_df.dropna(axis=1, how='all')

    # Calculate weighted scores (as percentage of max points)
    for col in filtered_df.columns:
        if " - Max Points" in col:  # Identify max points columns
            # Get corresponding score column
            assignment_col = col.replace(" - Max Points", "")
            if assignment_col in filtered_df.columns:  # Ensure the score column exists
                filtered_df[f"Weighted_{assignment_col}"] = (
                    filtered_df[assignment_col] / filtered_df[col]) * 100

    return filtered_df


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
    filtered_df.loc[:, 'Z_Bin'] = (filtered_df['Z_Score'] // bin_size) * bin_size

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
    print(f"Histogram saved as {output_file}")

    return fig


def run_analysis(csv_path: str,
                 target_assignments: Optional[List[str]] = None,
                 predictor_assignments: Optional[List[str]] = None,
                 target_category_name: Optional[str] = None,
                 predictor_category_name: Optional[str] = None,
                 auto_detect: bool = True):
    """
    Run the full analysis pipeline with clear reporting.

    Parameters:
    -----------
    csv_path : str
        Path to the CSV file
    target_assignments : Optional[List[str]]
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
    print(f"Loading and cleaning data from {csv_path}")
    df = clean_raw_csv(csv_path)

    # Detect categories if using auto-detection
    if auto_detect:
        categories = detect_assignment_categories(df)
        print("\nDetected assignment categories:")
        for category, assignments in categories.items():
            print(f"  {category.capitalize()}: {assignments}")

    # Use detected categories if not specified
    if target_assignments is None and auto_detect:
        target_assignments = categories['exams']
        if not target_category_name:
            target_category_name = "Exam"

    if predictor_assignments is None and auto_detect:
        predictor_assignments = categories['homeworks']
        if not predictor_category_name:
            predictor_category_name = "Homework"

    if not target_assignments:
        raise ValueError("No target assignments specified or detected")

    # Set default category names if not provided
    if not target_category_name:
        target_category_name = "Target"
    if not predictor_category_name:
        predictor_category_name = "Predictor"

    # Run prediction
    results, z_scores = calculate_predictions(
        df,
        target_assignments,
        predictor_assignments,
        target_category_name,
        predictor_category_name
    )

    # Plot histogram
    if not results.empty:
        title = f"Prediction Residuals: {target_category_name} from {predictor_category_name}"
        plot_z_score_histogram(results, title=title)

    return df, results, z_scores


# Example usage
if __name__ == "__main__":
    csv_path = "path"

    # Option 1: Auto-detect assignments and categories
    df, results, z_scores = run_analysis(csv_path, auto_detect=True)

    # Option 2: Explicitly specify everything
    # df, results, z_scores = run_analysis(
    #     csv_path,
    #     target_assignments=["Exam1", "Exam2"],
    #     predictor_assignments=["Hw1", "Hw2", "Hw3", "Hw4"],
    #     target_category_name="Exams",
    #     predictor_category_name="Homework Assignments",
    #     auto_detect=False
    # )
