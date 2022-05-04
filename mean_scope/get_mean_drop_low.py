import numpy as np


def get_mean_drop_low(perc, weight, drop_n=0):
    """ drops lowest assignment, returns weighted mean

    we skip any assignments whose perc or weight is nan

    note: this doesn't necessarily maximize grade with varying weight ... might
    be worth optimizing down the road but its not obvious (to me) how to do
    this

    Args:
        perc (np.array): percentage earned per assignment
        weight (np.array): weight of each assignment
        drop_n (int): number of assignments to drop
    Returns:
        mean (float): mean score, weighted by weight after having dropped the
            most damaging drop_n assignments
    """
    # cast to array & copy
    weight = np.array(weight)
    perc = np.array(perc)

    # drop nans
    idx_keep = np.logical_and(~np.isnan(weight),
                              ~np.isnan(perc))
    weight = weight[idx_keep]
    perc = perc[idx_keep]

    # drop a few assignments
    idx_keep = np.argsort(perc)[drop_n:]
    weight = weight[idx_keep]
    perc = perc[idx_keep]

    if not weight.size:
        # no assignments to average
        return np.nan

    # compute weighted average
    return np.inner(perc, weight) / weight.sum()
