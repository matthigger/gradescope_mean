# Gradescope Mean

Compute final grades from a Gradescope CSV export — with category weighting, lowest-N drops, late penalties, per-student waivers, and more.

    pip install gradescope-mean

## Quick Start

1. Download grades from Gradescope (`Assignments > Download Grades > CSV`) to a file like `scope.csv`.

2. Run:

        gradescope-mean grade scope.csv

   This produces [grade_full.csv](doc/grade_full.csv) and creates a `config.yaml` in the same directory.

3. Edit `config.yaml` to set up your grading policy (see [Configuration](#configuration) below), then re-run:

        gradescope-mean grade scope.csv --config config.yaml

That's it. The rest of this README covers what you can put in that config file and the additional flags available.

## Configuration

All of the interesting behavior lives in `config.yaml`. On your first run a default copy is created for you — open it up and fill in the sections that apply to your course. The full reference is in [doc/config.md](doc/config.md); here's a summary of what's available:

### Category weights & drops

Group assignments into categories and weight them independently. Drop each student's lowest N scores in a category.

```yaml
category:
  weight:
    hw: 50
    exam: 50
  drop_low:
    hw: 2          # drop each student's 2 lowest HW scores
```

Assignments are mapped to categories by substring match (case/space-insensitive), so an assignment named "HW 3" lands in the `hw` category automatically.

### Late penalties

Penalize late submissions per day, with a configurable number of excused "free" late days per student. Individual students can receive extra (or fewer) excused days for accommodations.

```yaml
category:
  late_penalty:
    hw:
      penalty_per_day: 0.15    # 15% of an average HW per unexcused day
      excuse_day: 3            # 3 free late days across all HWs
      excuse_day_offset:
        student@uni.edu: 2     # this student gets 5 total (3 + 2)
```

### Waivers

Waive specific assignments (and their late penalties) for individual students — the final grade is computed as if the assignment was never assigned:

```yaml
waive:
  student@uni.edu: hw1, hw2
```

Or waive only the late penalty on specific assignments (the score still counts):

```yaml
waive_late:
  student@uni.edu: hw3
```

### Exclude & substitute assignments

Exclude assignments entirely, or set a minimum completion threshold to auto-exclude unfinished work:

```yaml
assignments:
  exclude:
    - practice_quiz
  exclude_complete_thresh: 0.6   # drop assignments < 60% submitted
```

Substitute one assignment's score with the best of several alternatives (useful for merging multiple quiz versions):

```yaml
assignments:
  substitute:
    quiz1:
      - quiz1_v2
      - quiz1_v3
  exclude:
    - quiz1_v2
    - quiz1_v3
```

### Grade thresholds & email validation

Set letter-grade cutoffs and provide an email list to flag students who may have dropped the course:

```yaml
grade_thresh:
  0.93: A
  0.90: A-
  # ... (sensible defaults are provided)

email_list:
  - active_student@uni.edu
```

See [doc/config.md](doc/config.md) for the complete reference with all options and defaults.

## Additional Options

All flags go on the `grade` subcommand. Run `gradescope-mean grade --help` for the full list.

```bash
# choose where the output CSV goes
gradescope-mean grade scope.csv --config config.yaml -o final_grades.csv

# generate a histogram of grades per category
gradescope-mean grade scope.csv --config config.yaml --plot

# generate a PCA scatter plot (spot outliers / trends)
gradescope-mean grade scope.csv --config config.yaml --pca

# export a CSV of late days per student-assignment pair
gradescope-mean grade scope.csv --config config.yaml --late_csv late_days.csv

# create per-student CSVs (handy for emailing individual breakdowns)
gradescope-mean grade scope.csv --config config.yaml --per_student

# suppress status messages
gradescope-mean grade scope.csv --config config.yaml -q

# force a fresh default config (existing one is kept with a timestamp)
gradescope-mean grade scope.csv --new-config
```

`--plot` and `--pca` accept an optional filename (e.g. `--plot my_hist.html`); without one they default to `hist.html` and `pca.html`.

### Histogram output

<img alt="histogram per category" src="doc/hist.png" width="800px"/>

## Exporting Grades

The `grade` command produces a `grade_full.csv`. Two additional subcommands format it for upload to your LMS:

### Canvas

```bash
gradescope-mean canvas grade_full.csv canvas.csv --scale100
```

Download your Canvas gradebook as `canvas.csv` first. The `--scale100` flag scales grades to 0–100 to avoid Canvas's 2-decimal-place rounding ambiguity. See [doc/upload_canvas.md](doc/upload_canvas.md) for details.

### Banner (Northeastern)

```bash
gradescope-mean banner grade_full.csv 202310 -c 12345 -c 67890
```

Pass the term code and one or more CRNs. Produces a timestamped `.xlsx` ready for Banner import. See [doc/upload_banner.md](doc/upload_banner.md) for details.
