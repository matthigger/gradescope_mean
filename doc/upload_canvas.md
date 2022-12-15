# Uploading processed grades (`grade_full.csv`) to Canvas

Download a canvas gradebook as some `.csv` and pass it into our grading script:

    python -m gradescope_mean scope.csv --canvas canvas.csv

The script will merge the grades and means into a new `canvas_<timestamp>.csv`
file which can be imported to canvas.

We'll print a list of students who didn't match between the gradebooks (either from canvas or our own gradescope-derived csv).

## Notes
- Canvas didn't take any string data as a grade (i.e. "letter") for me (Dec
  2022)
- Canvas displays to two rounded decimal places on the website, good to know for students whose grades are on the cusp between two letter grades

## Complaint
This approach, downloading and modifying a canvas template is cumbersome but I
don't see a better way: canvas has some internal ID which the gradescope csv doesn't have and canvas won't accept grades without this ID ... even though it's redundant with SIS User ID.  