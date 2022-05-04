from math import ceil

import numpy as np
import pandas as pd

from .assign_list import AssignmentList


class Gradebook:
    """ a grade for every student-assignment pair & manipulations

    Attributes:
        df (pd.DataFrame): index is email of student and each col is assignment
            values are percentage student earned (nan for waived).  contains
            a few metadata columns too (first name, last name, section, id)

        df_lateday (pd.DataFarme): index are email, cols are assignment and
            values are days each assignment is late
        ass_list (AssignmentList): a list of assignments
        points (np.array): points per assignment (same order as ass_list)
    """

    def __init__(self, f_scope):
        df_scope = pd.read_csv(f_scope, index_col='Email')

        # lowercase input data
        meta_data_cols = 4
        for idx in range(meta_data_cols):
            df_scope.iloc[:, idx] = \
                df_scope.iloc[:, idx].map(lambda x: str(x).lower())
        df_scope.index.map(str.lower)
        df_scope.index.name = df_scope.index.name.lower()
        df_scope.columns = [s.lower() for s in df_scope.columns]
        df_scope.fillna(0, inplace=True)

        # compute percent per assignment & points
        self.ass_list = AssignmentList(df_scope.columns)
        self.df = pd.DataFrame()
        self.points = np.empty(len(self.ass_list))
        for idx, ass in enumerate(self.ass_list):
            # points per assignment
            ass_max_pt = ass + self.ass_list.MAX_PTS
            assert len(df_scope[ass_max_pt].unique()) == 1, \
                f'multiple max pts: {ass}'
            self.points[idx] = df_scope[ass_max_pt].values[0]

            # percentage per assignment
            self.df[ass] = df_scope[ass] / df_scope[ass_max_pt]

        # compute days late
        def get_days_late(s_hour_min_sec):
            # grace period of 1 hour built in (we ignore min / sec)
            return ceil(float(s_hour_min_sec.split(':')[0]) / 24)

        self.df_lateday = pd.DataFrame()
        for ass in self.ass_list:
            ass_late = ass + self.ass_list.LATE
            self.df_lateday[ass] = df_scope[ass_late].map(get_days_late)

    def waive(self, waive_dict):
        """ waives assignments by marking percentages as nan

        Args:
            waive_dict (dict): keys are emails, values are strings of comma
                seperated assignments (e.g. 'hw1, hw2')
        """

        for email, ass_many in waive_dict.items():
            for ass in ass_many.split(','):
                self.df.loc[email, self.ass_list.normalize(ass)] = np.nan

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
            new_col_dict[ass_to] = self.df.loc[:, ass_from_list].max(axis=1)

        # substitute
        for ass_to, s in new_col_dict.items():
            self.df[ass_to] = s
