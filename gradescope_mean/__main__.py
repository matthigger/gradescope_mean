#!/usr/bin/env python3

import argparse
import pathlib

import gradescope_mean

parser = argparse.ArgumentParser(
    description='grade synthesis from gradescope (see doc at: https://github.com/matthigger/gradescope_mean/blob/main/readme.md)')
parser.add_argument('f_scope', type=str,
                    help='gradescope output csv (Assignments > Download Grades > CSV)')
parser.add_argument('--config', dest='f_config', action='store',
                    default=None,
                    help='yaml configuration (see doc at: https://github.com/matthigger/gradescope_mean/blob/main/doc/config.md)')
parser.add_argument('--plot', dest='plot_flag', action='store',
                    default=True, help='toggles histogram plot per '
                                       'assignment category')
parser.add_argument('--canvas', dest='f_canvas', action='store',
                    default=None,
                    help='csv of grades downloaded from canvas (see doc at: https://github.com/matthigger/gradescope_mean/blob/main/doc/canvas.md ')
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

# plot
if args.plot_flag:
    fig = gradescope_mean.plot_hist(df_grade_full=df_grade_full,
                                    cat_weight_dict=config.cat_weight_dict)
    f_html = folder / f'hist.html'
    fig.write_html(str(f_html), include_plotlyjs='cdn')

# canvas
if args.f_canvas is not None:
    gradescope_mean.canvas_merge(f_canvas=args.f_canvas,
                                 df_grade_full=df_grade_full,
                                 meta_col_list=gradebook.df_meta.columns)
