from copy import copy
from math import ceil

import numpy as np
import pandas as pd

from .assign_list import AssignmentList
from .get_mean_drop_low import get_mean_drop_low


class Gradebook:
    """ a grade for every student-assignment pair & manipulations

    Attributes:
        df_perc (pd.DataFrame): index is email of student and each col is assignment
            values are percentage student earned (nan for waived).
        df_meta (pd.DataFrame): index is email, columns are metadata (first
            name, last name, section, id)
        df_lateday (pd.DataFarme): index are email, cols are assignment and
            values are days each assignment is late
        ass_list (AssignmentList): a list of assignments
        points (np.array): points per assignment (same order as ass_list)
    """
    META_DATA_COLS = 4

    def __init__(self, f_scope):
        df_scope = pd.read_csv(f_scope, index_col='Email')

        # groom input data
        df_scope.columns = [s.lower() for s in df_scope.columns]
        for idx in range(self.META_DATA_COLS):
            if df_scope.columns[idx] == 'sid':
                # student ids are ints, lets not cast to str
                continue
            df_scope.iloc[:, idx] = df_scope.iloc[:, idx].map(str.lower)
        df_scope.index.map(str.lower)
        df_scope.index.name = df_scope.index.name.lower()
        df_scope.fillna(0, inplace=True)

        # store meta data
        self.df_meta = df_scope.iloc[:, :self.META_DATA_COLS]

        # compute percent per assignment & points
        self.ass_list = AssignmentList(df_scope.columns)
        self.df_perc = pd.DataFrame()
        self.points = np.empty(len(self.ass_list))
        for idx, ass in enumerate(self.ass_list):
            # points per assignment
            ass_max_pt = ass + self.ass_list.MAX_PTS
            assert len(df_scope[ass_max_pt].unique()) == 1, \
                f'multiple max pts: {ass}'
            self.points[idx] = df_scope[ass_max_pt].values[0]

            # percentage per assignment
            self.df_perc[ass] = df_scope[ass] / df_scope[ass_max_pt]

        # compute days late
        def get_days_late(s_hour_min_sec):
            # grace period of 1 hour built in (we ignore min / sec)
            return ceil(float(s_hour_min_sec.split(':')[0]) / 24)

        self.df_lateday = pd.DataFrame()
        for ass in self.ass_list:
            ass_late = ass + self.ass_list.LATE
            self.df_lateday[ass] = df_scope[ass_late].map(get_days_late)

    def waive(self, waive_dict):
        """ waives assignment (per student) by marking percentages as nan

        Args:
            waive_dict (dict): keys are emails, values are strings of comma
                seperated assignments (e.g. 'hw1, hw2')
        """

        for email, ass_many in waive_dict.items():
            for ass in ass_many.split(','):
                self.df_perc.loc[email, self.ass_list.normalize(ass)] = np.nan

    def substitute(self, sub_dict):
        """ substitutes some assignment percentages (if sub is higher)

        This method is useful when there are multiple versions of a quiz, each
        with their own gradescope assignment.  It allows you to consolidate
        them into a single assignment (be sure to exclude the substituted
        assignments so they don't count)

        Args:
            sub_dict (dict): keys are target assignment, values are list of
                all assignments which could be substituted
        """
        # we keep all the new, substituted grades in a dict before substituting
        # (were we to substitute, the order of substitutions could cause issue)
        new_col_dict = dict()
        for ass_to, ass_from_list in sub_dict.items():
            if ass_to not in ass_from_list:
                # ensure ass_to is in the list of potential substitutes
                ass_from_list = ass_from_list + [ass_to]

            # get max percentage across all assignments, substitute it
            new_col_dict[ass_to] = self.df_perc.loc[:, ass_from_list].max(
                axis=1)

        # substitute
        for ass_to, s in new_col_dict.items():
            self.df_perc[ass_to] = s

    def remove(self, ass):
        """ deletes an assignment

        Args:
            ass (s): an assignments to remove from gradebook
        """
        # normalize assignment name
        ass = self.ass_list.normalize(ass)
        ass_idx = self.ass_list.index(ass)

        # remove
        del self.df_perc[ass]
        del self.df_lateday[ass]
        self.ass_list.pop(ass_idx)
        self.points = np.delete(self.points, ass_idx)

    def average(self, cat_weight_dict=None):
        """ final grades, weighted by points (default) or category weights

        Args:
            cat_weight_dict (dict): keys are strings which define categories
                values are unnormalized (positive) weights assigned to each
                category.  (e.g. if HW / exam each worth 50% of grade then
                cat_weight_dict {'hw': 50, 'exam': 50}.  Assignment names must
                each contain exactly one category such that categories
                partition all assignments.  (Default: no categories given, each
                assignment weighted by points given on gradescope)

        Returns:
            df_grade (pd.DataFrame): contains self.df_perc with added columns of
                weighted mean (and mean of any category)
        """
        if cat_weight_dict is None:
            # all assignments contain ''
            cat_weight_dict = {'': 1}

        # extract percentages as array (a bit quicker)
        perc_all = self.df_perc.iloc[:, self.META_DATA_COLS:].values

        df_grade = copy(self.df_perc)
        for cat, weight in cat_weight_dict.items():
            # boolean index into assignments of given category
            cat_bool = np.array([cat in ass for ass in self.ass_list])
            perc_cat = perc_all[:, cat_bool]
            weight_cat = self.points_cat[:, cat_bool]

            for idx, email in enumerate(self.df_perc.index):
                # compute mean per student-category
                s_mean = f'mean_{cat}'
                _perc = perc_cat[idx, :]
                _weight = weight_cat[idx, :]
                df_grade.loc[email, s_mean] = get_mean_drop_low(_perc, _weight)

        return df_grade
