#!/usr/bin/env python3

import argparse
import pathlib

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import gradescope_mean

parser = argparse.ArgumentParser(
    description='grade synthesis from gradescope (see doc at: https://github.com/matthigger/gradescope_mean/blob/main/readme.md)')
parser.add_argument('f_scope', type=str,
                    help='gradescope output csv (Assignments > Download Grades > CSV)')
parser.add_argument('--config', dest='f_config', action='store',
                    default=None, help='yaml configuration (see doc at: https://github.com/matthigger/gradescope_mean/blob/main/doc/config.md)')
parser.add_argument('--plot', dest='plot_flag', action='store',
                    default=True, help='toggles histogram plot per '
                                       'assignment category')

# load gradescope data
args = parser.parse_args()

# load config
folder = pathlib.Path(args.f_scope).resolve().parent
if args.f_config is None:
    config = gradescope_mean.Config.cli_copy_config(folder)
else:
    config = gradescope_mean.Config.from_file(args.f_config)

# process
gradebook, df_grade_full = config(f_scope=args.f_scope)

# output
df_grade_full.to_csv(str(folder / 'grade_full.csv'))

if args.plot_flag:
    # always plot mean grade histogram
    feat_list = ['mean']
    if config.cat_weight_dict is not None:
        # plot histogram per category (if specified)
        feat_list += [f'mean_{feat}' for feat in config.cat_weight_dict.keys()]

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
    f_html = folder / f'hist.html'
    fig.write_html(str(f_html), include_plotlyjs='cdn')
