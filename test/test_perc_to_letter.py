from gradescope_mean.perc_to_letter import *


def test_val_to_letter():
    val_letter_list = [(1, 'A'), (.9, 'A-'), (.91, 'A-'), (.6, 'D-'),
                       (np.nan, 'no-grade')]

    for val, letter_exp in val_letter_list:
        letter = perc_to_letter(val)
        assert letter == letter_exp, f'error in perc_to_letter: {val}'
