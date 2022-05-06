import numpy as np

GRADE_THRESH = {'A': .93,
                'A-': .90,
                'B+': .87,
                'B': .83,
                'B-': .80,
                'C+': .77,
                'C': .73,
                'C-': .70,
                'D+': .67,
                'D': .63,
                'D-': .60,
                'E': 0}


def perc_to_letter(perc, grade_thresh=None, float_bonus=1e-8):
    """ converts a percentage to a letter grade

    Args:
        perc (float): percentage (on assignment)
        grade_thresh (dict): keys are letter grades, values are lower
            thresholds (inclusive) to get grade
        float_bonus (float): due to floating point rounding errors, we give all
            students a slight bonus to ensure they don't miss out on any
            thresholds their grades meet their floating point average may just
            fall short of

    Returns:
        grade (str): letter grade
    """
    if grade_thresh is None:
        # default
        grade_thresh = GRADE_THRESH

    if np.isnan(perc):
        return 'no-grade'

    for mark, thresh in grade_thresh.items():
        if perc + float_bonus >= thresh:
            return mark

    raise
