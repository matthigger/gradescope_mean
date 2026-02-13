# Gradescope Mean

A utility which computes final grades (example: [grade_full.csv](doc/grade_full.csv)) from Gradescope exports. It allows the instructor to ...

- weight assignments per category
    - e.g. all HW assignments are 50% of grade
- drop lowest N assignments per category
    - e.g. 2 lowest HW assignments, per student, are dropped
- apply a late penalty (per day) that assignments are submitted beyond deadline
    - e.g. HW is penalized 15% of average assignment hw weight for every day late it is submitted
    - includes support for not penalizing the first N "late days" per assignment category (e.g. each student may use up to 3 "late days" across all HWs without penalty)
    - per-student adjustments to excused late days
- waive assignments per individual student
- waive late penalties per individual student's assignment
- validate the Gradescope student list against an email list of active students
    - e.g. one student has a low average grade — have they dropped the course?
- exclude assignments which shouldn't be included in final grade
    - assignments automatically excluded if they don't have some minimum completion threshold
- substitute one assignment in place of another (where substitute has higher percentage)
    - e.g. to "merge" two versions of the quiz with their own unique Gradescope assignment
        1. substitute `quiz_02` for `quiz_01`
        2. exclude `quiz_02`
- convert final percentages to letter grades with configurable thresholds

# Installation

    pip install gradescope-mean

# Quick Start

Download all Gradescope assignments to a local `scope.csv` file
(`Assignments > Download Grades > Download CSV`) and run:

    gradescope-mean grade scope.csv

This creates [grade_full.csv](doc/grade_full.csv) using the default configuration.
On the first run a `config.yaml` is automatically created in the same directory as your CSV — edit it to take advantage of the features listed above (details in the [configuration doc](doc/config.md)).

To re-run with your configuration:

    gradescope-mean grade scope.csv --config config.yaml

# CLI Reference

The tool uses subcommands: `grade`, `canvas`, and `banner`. Run `gradescope-mean --help` to see them all, or `gradescope-mean <subcommand> --help` for details on any one.

## `gradescope-mean grade`

The main workflow — compute final grades from a Gradescope CSV.

```
gradescope-mean grade scope.csv [OPTIONS]
```

| Flag | Description |
|---|---|
| `--config FILE` | Path to a YAML config file. If omitted, uses `config.yaml` in the CSV's directory (creates a default copy if none exists). |
| `--new-config` | Force creation of a fresh default `config.yaml`, even if one already exists (the existing file is preserved with a timestamp). |
| `-o`, `--output FILE` | Output CSV path. Default: `grade_full.csv` in the same directory as the input CSV. |
| `--plot [FILE]` | Generate a histogram HTML per assignment category. Default filename: `hist.html`. |
| `--pca [FILE]` | Generate a PCA scatter plot HTML. Default filename: `pca.html`. |
| `--late_csv FILE` | Output a CSV of late days per student-assignment pair. |
| `--per_student` | Output a CSV per student into a `per_student/` folder. Useful for emailing students the details of their grades. |
| `-q`, `--quiet` | Suppress informational output. |
| `--version` | Print version and exit (top-level flag: `gradescope-mean --version`). |

### Examples

```bash
# basic run, auto-creates config.yaml on first use
gradescope-mean grade scope.csv

# explicit config, custom output path, quiet
gradescope-mean grade scope.csv --config config.yaml -o final_grades.csv -q

# generate histogram and PCA plots with default filenames
gradescope-mean grade scope.csv --config config.yaml --plot --pca

# generate histogram with a custom filename
gradescope-mean grade scope.csv --config config.yaml --plot my_histogram.html

# per-student CSVs and late-day report
gradescope-mean grade scope.csv --config config.yaml --per_student --late_csv late_days.csv

# force a fresh default config (existing config.yaml is preserved with a timestamp)
gradescope-mean grade scope.csv --new-config
```

### Histogram Output

Pass `--plot` to view histograms ([hist.html](doc/hist.html)) per assignment category:

<img alt="histogram per category" src="doc/hist.png" width="800px"/>

# Exporting Grades

The `grade` command produces a `grade_full.csv` which can be further processed for upload to [Canvas](doc/upload_canvas.md) or [Northeastern's Banner](doc/upload_banner.md).

## `gradescope-mean canvas`

Merge grades into a Canvas-compatible CSV for upload.

```
gradescope-mean canvas grade_full.csv canvas.csv [OPTIONS]
```

| Flag | Description |
|---|---|
| `--scale100` | Scale grades by 100 (0–100 range) to avoid Canvas rounding ambiguity at 2 decimal places. |
| `-q`, `--quiet` | Suppress informational output. |

Download your Canvas gradebook as `canvas.csv`, then:

```bash
gradescope-mean canvas grade_full.csv canvas.csv --scale100
```

This produces a timestamped `canvas_<timestamp>.csv` ready for Canvas import. See the [Canvas upload doc](doc/upload_canvas.md) for details.

## `gradescope-mean banner`

Prepare an Excel file for Banner upload.

```
gradescope-mean banner grade_full.csv TERM_CODE -c CRN [OPTIONS]
```

| Flag | Description |
|---|---|
| `-c`, `--crn CRN` | CRN of a course section. May be passed multiple times for multiple sections. |
| `-q`, `--quiet` | Suppress informational output. |

```bash
# single section
gradescope-mean banner grade_full.csv 202310 -c 12345

# multiple sections
gradescope-mean banner grade_full.csv 202310 -c 12345 -c 67890
```

This produces a timestamped `grade_full_banner_<timestamp>.xlsx`. See the [Banner upload doc](doc/upload_banner.md) for details.

# Migration from `python -m`

Prior versions used `python -m gradescope_mean scope.csv`. The new CLI uses subcommands:

| Old | New |
|---|---|
| `python -m gradescope_mean scope.csv` | `gradescope-mean grade scope.csv` |
| `python -m gradescope_mean scope.csv --config config.yaml` | `gradescope-mean grade scope.csv --config config.yaml` |
| `python -m gradescope_mean.canvas grade_full.csv canvas.csv` | `gradescope-mean canvas grade_full.csv canvas.csv` |
| `python -m gradescope_mean.banner grade_full.csv 202310 -c 12345` | `gradescope-mean banner grade_full.csv 202310 -c 12345` |

The interactive prompt that asked whether to use an existing `config.yaml` has been replaced: the existing file is now used automatically (pass `--new-config` to force a fresh copy instead).
