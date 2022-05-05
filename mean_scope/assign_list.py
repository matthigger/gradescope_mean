class AssignmentNotFoundError(NameError):
    pass


class AssignmentList(list):
    """ normalizes assignment names """
    MAX_PTS = ' - max points'
    LATE = ' - lateness (h:m:s)'

    def __init__(self, columns):
        ass_list = [col.replace(self.MAX_PTS, '').lower() for col in columns
                    if self.MAX_PTS in col]
        super().__init__(sorted(ass_list))

    def match_multi(self, s_assign, max_pts=False):
        """ given str, finds all matching assignment in list (containing str)

        Args:
            s_assign (str): input string to match to assignment
            max_pts (bool): if True, will add MAX_PTS to output

        Returns:
            s_assign_tup (tup): all matching assignments
        """
        s_assign = s_assign.lower().strip()
        s_assign_tup = tuple(col for col in self if s_assign in col)

        if max_pts:
            # add max points
            s_assign_tup = tuple(s + self.MAX_PTS for s in s_assign_tup)

        return s_assign_tup

    def match(self, s_assign, **kwargs):
        """ finds the unique match to an assignment"""
        # get all matches
        s_assign_tup = self.match_multi(s_assign, **kwargs)

        # ensure match is unique
        if len(s_assign_tup) != 1:
            s_error = f'no unique assignment: {s_assign} in {s_assign_tup}'
            raise AssignmentNotFoundError(s_error)

        return s_assign_tup[0]
