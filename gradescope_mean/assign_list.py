class AssignmentNotFoundError(NameError):
    pass


class AssignmentList(list):
    """ lookup assignment string with partial match without spaces or capitals

    the keys of the dictionary are the normalized names, the values are the
    full names.
    """
    MAX_PTS = ' - max points'
    LATE = ' - lateness (h:m:s)'

    def __init__(self, columns):
        ass_list = [col.replace(self.MAX_PTS, '') for col in columns
                    if self.MAX_PTS in col]
        ass_norm_list = [self.normalize(ass) for ass in ass_list]
        assert len(ass_norm_list) == len(set(ass_norm_list)), \
            'two assignment names differ by only capitalization or spacing'
        super().__init__(sorted(ass_list))

    @classmethod
    def normalize(cls, s):
        """ removes spaces, makes lowercase """
        return s.replace(' ', '').lower()

    def match_iter(self, s_assign):
        """ iterates through all matching assignments

        Args:
            s_assign (str): input string to match to assignment

        Returns:
            s_assign_tup (tup): all matching assignments
        """
        ass_search_norm = self.normalize(s_assign)

        for ass in self:
            if ass_search_norm in self.normalize(ass):
                yield ass

    def match(self, s_assign):
        """ finds the unique match to an assignment"""
        # get all matches
        s_assign_tup = tuple(self.match_iter(s_assign))

        # ensure match is unique
        if len(s_assign_tup) != 1:
            s_error = f'no unique assignment: {s_assign} in {s_assign_tup}'
            raise AssignmentNotFoundError(s_error)

        return s_assign_tup[0]
