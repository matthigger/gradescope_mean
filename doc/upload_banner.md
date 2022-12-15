# Uploading to Banner

By first selecting a course (click on a row) and then clicking the "gear" in the top right you can "import" grades to Banner for that course:

<img src="banner.png" width=800>

Banner will accept an `xls` file and allow you to associate columns from your input to the necessary banner fields.  If all three of the following banner fields match a student in the selected course then the remaining fields (e.g. any column you choose as a "Final Grade") is uploaded for that student:
- CRN (5 digits)
- Term Code (6 digits)
  - e.g. "202310" for the third row of the image above
- Student ID (9 digits)
  - should not include the "S" suffix often on NUIDs

If a record in the uploaded `xls` doesn't match all three fields above, a warning is thrown.

## Expected Workflow
- in a spreadsheet application:
  - Add a CRN and Term Code to `grade_full.csv`
  - save it as an `xls` file
- upload to banner

## Multiple Sections "Trick"
It can be challenging to easily get the proper CRN for each student, which varies across sections.
Instead, a common trick is to set a constant CRN across all students when uploading to that CRN's section and rely on banner to discard irrelevant students with warnings.