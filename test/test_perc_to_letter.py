from gradescope_mean.perc_to_letter import *

GRADE_THRESH_UNORDERED = {.00: 'E',
                          .93: 'A',
                          .90: 'A-',
                          .87: 'B+',
                          .83: 'B',
                          .80: 'B-',
                          .77: 'C+',
                          .73: 'C',
                          .70: 'C-',
                          .67: 'D+',
                          .63: 'D',
                          .60: 'D-'}


def test_val_to_letter():
    val_letter_list = [(1, 'A'), (.9, 'A-'), (.91, 'A-'), (.6, 'D-'),
                       (np.nan, 'no-grade')]

    for val, letter_exp in val_letter_list:
        letter = perc_to_letter(val)
        assert letter == letter_exp, f'error in perc_to_letter: {val}'

        letter = perc_to_letter(val, grade_thresh=GRADE_THRESH_UNORDERED)
        assert letter == letter_exp, f'error in perc_to_letter: {val}'
