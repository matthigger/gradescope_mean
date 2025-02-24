import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_hist(df_grade_full, cat_weight_dict):
    """ plots a histogram of grades

    example:
    https://github.com/matthigger/gradescope_mean/blob/main/doc/hist.png

    Args:
        df_grade_full (pd.DataFrame):
        cat_weight_dict (dict): keys are categories, values are weights

    Returns:
        fig (plotly):
    """

    # always plot mean grade histogram
    feat_list = ['mean']
    if cat_weight_dict is not None:
        # plot histogram per category (if specified)
        feat_list += [f'mean_{feat}' for feat in cat_weight_dict.keys()]

    # make histogram subplots
    fig = make_subplots(cols=len(feat_list), rows=1, subplot_titles=feat_list)
    for col_idx, feat in enumerate(feat_list):
        trace = go.Histogram(y=df_grade_full[feat], name='feat',
                             ybins=dict(start=.5, end=1, size=.025),
                             opacity=0.75)
        fig.append_trace(trace, col=col_idx + 1, row=1)

        mean = df_grade_full[feat].mean()
        fig.add_hline(y=mean, annotation_text=f'mean: {mean:.3f}',
                      col=col_idx + 1, row=1)
    fig.update_layout(showlegend=False)

    return fig


def plot_pca(df_grade_full, cat_weight_dict):
    """ plots scatter of students on 1st 2 PCA directions

    (helps identify trends between assignments and spot outliers, likely hw
    and exam scores are correlated, but maybe some sub-group have abnormally
    high hw

    Args:
        df_grade_full (pd.DataFrame):
        cat_weight_dict (dict): keys are categories, values are weights

    Returns:
        fig (plotly):
    """
    if cat_weight_dict is not None:
        print('warning: category weight not accounted for, each assignment '
              'given equal weight')

    # kludge: assignments are all columns after 'letter'
    idx_letter = list(df_grade_full.columns).index('letter')
    df = df_grade_full.iloc[:, idx_letter + 1:].copy()

    # center and impute
    df -= df.mean()
    df = df.fillna(0)

    # pca projection
    x = df.values
    c = np.cov(x.T)
    vals, vecs = np.linalg.eig(c)

    # ensure pca vectors largely point "positive" (top right is for strong
    # students in resulting graph)
    flip = (vecs > 0).sum(axis=0) > x.shape[1] / 2
    vecs = vecs @ np.diag(flip)

    # prep p
    df = df_grade_full.copy()
    df['pca0'] = x @ vecs[:, 0]
    df['pca1'] = x @ vecs[:, 1]
    fig = px.scatter(df,
                     x='pca0',
                     y='pca1',
                     hover_data=df.columns)

    return fig