#!/usr/bin/env python3

import argparse
import pathlib

import mean_scope

parser = argparse.ArgumentParser(
    description='grade synthesis from gradescope (todo: githib link)')
parser.add_argument('f_scope', type=str,
                    help='gradescope output csv (Assignments > Download Grades > CSV)')
parser.add_argument('--config', dest='f_config', action='store',
                    default=None, help='yaml configuration (see todo: link)')

# load gradescope data
args = parser.parse_args()

# load config
folder = pathlib.Path(args.f_scope).resolve().parent
if args.f_config is None:
    config = mean_scope.Config.cli_copy_config(folder)
else:
    config = mean_scope.Config.from_file(args.f_config)

# process
gradebook, df_grade_full = config(f_scope=args.f_scope)

# output
df_grade_full.to_csv(str(folder / 'grade_full.csv'))
