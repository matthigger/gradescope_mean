class AssignmentNotFoundError(NameError):
    pass


class AssignmentList(list):
    """ normalizes assignment names """
    MAX_PTS = ' - max points'

    def __init__(self, columns):
        ass_list = [col.replace(self.MAX_PTS, '').lower() for col in columns
                    if self.MAX_PTS in col]
        super().__init__(sorted(ass_list))

    def normalize(self, s_assign, max_pts=False):
        """ given string, finds matching assignment in list

        Args:
            s_assign (str): input string to match to assignment
            max_pts (bool): if True, will add MAX_PTS to output

        Returns:
            s_assign (str): assignment, now matched to a unique entry in list
        """
        s_assign = s_assign.lower().strip()
        s_assign_norm_list = [col for col in self if s_assign in col]
        if len(s_assign_norm_list) != 1:
            s_error = f'no unique assignment: {s_assign} in {s_assign_norm_list}'
            raise AssignmentNotFoundError(s_error)

        s_norm = s_assign_norm_list[0]
        if max_pts:
            # add max points
            s_norm += self.MAX_PTS

        return s_norm
