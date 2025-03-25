import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from gradescope_mean.assign_list import AssignmentList


def predict(df, ass_target, ass_predict=None):
    """ predicts a single assignment from others (linear regression)

    assuming the regression works well (high enough r^2), then we're
    interested in the z score of the residual.  a student whose exam score is
    2 std dev below expected might really have some exam anxiety.
    alternatively a high z score indicates a student who isn't putting much
    effort into their HW, or might have received some other advantage not
    accounted for in the exam

    Args:
        df: (pd.DataFrame) input scores.  we expect users will load the csv
            `grade_full.csv`, though any work.
        ass_target: (str) string which is used to match a single column in
            input dataframe
        ass_predict: (str) any column which this string will be used to predict
            the target assignment.  if nothing passed, all assignments used

    Returns:
        coef_dict (dict): keys are other assignments, values are
            coefficients in linear regression
        r2_score (float): r2 score of regression (not cross validated)
        df_out (pd.DataFrame): index is same as input.  columns output are
            true, pred, z_score
    """
    ass_list = AssignmentList(df.columns, require_max_pts=False)

    # handle missing data (missing targets dropped, all others mean imputed)
    ass_target = ass_list.match(ass_target)
    df = df.dropna(subset=[ass_target])
    df.fillna(df.mean(), inplace=True)

    # get series corresponding to target
    s_y = df[ass_target]

    # get dataframe corresponding to predictor features
    if ass_predict is not None:
        # use matching features
        ass_predict_list = list(ass_list.match_iter(ass_predict))
        df_x = df[ass_predict_list]
    else:
        # use all features
        df_x = df

    # add bias feature
    df_x.insert(0, 'bias', 1)

    # don't use target feature as a predictor!
    if ass_target in df_x.columns:
        df_x = df_x.drop(ass_target, axis=1)

    # extract values for linear algebra
    x = df_x.values
    y = s_y.values

    # Project y to estimates using pseudoinverse
    coef = np.linalg.pinv(x) @ y
    y_hat = x @ coef
    resid = y - y_hat
    r2 = 1 - np.var(resid) / np.var(y)
    z = resid / np.std(resid)

    # warn on funky regressions
    if np.isclose(np.var(y), 0):
        warnings.warn(f'invalid z scores: target assignment {ass_target} has '
                      f'constant score')
    elif np.isclose(np.var(resid), 0):
        warnings.warn(f'constant residual, are predictor assignments '
                      f'constant across students?')

    # outputs result DataFrame
    df_out = pd.DataFrame({'true': y, 'pred': y_hat, 'z': z},
                          index=df.index)
    coef_dict = dict(zip(df_x.columns, coef))

    return coef_dict, r2, df_out


def plot_z_score_histogram(df: pd.DataFrame, z_min: float = -5,
                           z_max: float = 4,
                           bin_size: float = 0.5,
                           output_file: str = "histogram.html",
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
                                          filtered_df[
                                              'Z_Score'] // bin_size) * bin_size

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
