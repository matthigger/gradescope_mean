All configuration options are stored in a `.yaml` file which can be passed as:

    $python -m gradescope_mean scope.csv --config config.yaml

Remember that tabs aren't allowed in YAML so be sure to use spaces (either 2 or 4 per indent level, used consistently, will work).

# Category
## Category/Weight
    category:
        weight:
            quiz: 55
            hw: 45

A category is a subset of assignments (e.g. all homework assignments).   
The above configuration gives the `quiz` category 55% of the final grade weight and `hw` the remaining 45%.  
Weights needn't be unnormalized but should be positive.  
Assignments are mapped to categories by string comparison: each assignment should include the name of exactly one category (case-insensitive).  
By [default](../gradescope_mean/config.yaml), no categories are created and every assignment is weighted via its points on gradescope. 


## Category/Drop Low

    category: 
        drop low:
            hw: 1

The above configuration waives the lowest homework assignment per each student.  
Any category listed here must be included in the `category/weight` parameter above.  
By [default](../gradescope_mean/config.yaml) no assignments will be dropped from any category.

## Category/Late Penalty

    category:
        late_penalty:
            hw:
                penalty_per_day: .15
                excuse_day: 3
                excuse_day_adjust:
                    student0@northeastern.edu: 0
                    student1@northeastern.edu: 100

- `penalty_per_day: .15` implies that every unexcused [late day](https://help.gradescope.com/article/ude437e7li-faq-late-submissions) used to submit the work will be penalized by 15% of the points possible on an average homework assignment.  For example, if a single homework is 3 unexcused days late, it will lose 45% of the average homework points across all HW assignments.
  - Note the late penalty won't show on any single HW grade, but is 
    included in the `hw_mean` column of the output csv
  - A grace period of 1 hour is built into the computation of late days: a 
    late day needn't be used to excuse the first hour of every day 
    an assignment is late.
- `excuse_day: 3` provides every student 3 excused late days which will not 
  be penalized.  (I find this helpful to avoid too many emails over 
  deadline minutiae which always crops up ... I stole the idea from Kevin Gold)
- `excuse_day_adjust` allows you to adjust late days from `excuse_day` for individual students, helpful for DRC accommodations.

By [default](../gradescope_mean/config.yaml) no late penalty is applied to any category.

# Assignments

## Assignments/Exclude

    assignments:
        exclude:
            - dummy_quiz
            - quiz1_01

Excludes any assignment which includes the string `_dummy_quiz` or `quiz1_01` (case-insensitive comparison).  By [default](../gradescope_mean/config.yaml) no assignment is excluded.

## Assignments/exclude_complete_thresh

    assignments:
        exclude_complete_thresh: .6

Excludes an assignment when less than 60% of students received a non-zero score on the assignment (no submissions count as a zero score here).  Note this operation applied after other exclusions and substitutions (see above and below).  
By [default](../gradescope_mean/config.yaml) no assignment is excluded.

## Assignments/Substitute
    assignments:
        substitute:
            quiz1_01:
                - quiz1_02
                - quiz1_03

This replaces every student's `quiz1_01` score with the maximum percentage 
among `quiz1_01`, `quiz1_02` and `quiz1_03`.  Its helpful when you've got 
multiple versions of the same quiz in gradescope: each needs a unique 
rubric, but we want to consolidate them into a single assignment for the 
purposes of averaging into a final grade.  In this use case, be sure to also 
exclude `quiz1_02` and `quiz1_03` so they aren't included by themselves (they'll be substituted in for `quiz1_01` as needed before excluding).

By [default](../gradescope_mean/config.yaml) no assignments are substituted.

# Waive

    waive:
        student0@northeastern.edu: hw1
        student1@northeastern.edu: hw1, hw2, hw3

Waives assignments for individual students.  
For these students, the final grade is computed as if this work was never assigned.  
Should the student submit the assignment late, any late penalties are also waived.
By [default](../gradescope_mean/config.yaml) no assignments are waived.

# waive_late

    waive_late:
        student0@northeastern.edu: hw1
        student1@northeastern.edu: hw1, hw2, hw3

Waives any late penalties for the assignments per individual students.  This takes place before any excused late days are used.
By [default](../gradescope_mean/config.yaml) no late penalties are waived assignments are waived.

# Grade Thresh

    grade_thresh:
      .93: A
      .90: A-
      .87: B+
      .83: B
      .80: B-
      .77: C+
      .73: C
      .70: C-
      .67: D+
      .63: D
      .60: D-
      0: E

The lowest threshold (inclusive) to achieve a given grade.  Modify here if you'd like to "round" your student's final grades.

# Email_list

    email_list:
        - name0@northeastern.edu
        - name1@northeastern.edu
        - name2@northeastern.edu

If a list of email addresses is passed, we'll throw warnings if any is not found in the gradescope data.  Any student data from gradescope not in this list will be discarded without warning.  (This discarding is helpful as we ignore marks from students which are no longer in the course by keeping the email_list above up to date).

To avoid ambiguity around @husky.neu.edu / @northeastern.edu email addresses, comparisons will be made using only the portion of the email before the @ symbol.  

By [default](../gradescope_mean/config.yaml), every student in gradescope is used.