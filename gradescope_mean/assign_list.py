class AssignmentNotFoundError(NameError):
    pass


def normalize(s):
    """ removes spaces, makes lowercase """
    return s.replace(' ', '').lower()


class AssignmentList(list):
    """ lookup assignment string with partial match without spaces or capitals

    the keys of the dictionary are the normalized names, the values are the
    full names.
    """
    MAX_PTS = normalize(' - max points')
    LATE = normalize(' - lateness (h:m:s)')

    def __init__(self, ass_list):
        # normalize
        ass_norm_list = [normalize(ass) for ass in ass_list]
        ass_norm_list = [ass.replace(self.MAX_PTS, '') for ass in ass_norm_list
                         if self.MAX_PTS in ass]
        assert len(ass_norm_list) == len(set(ass_norm_list)), \
            'two assignment names differ by only capitalization or spacing'
        super().__init__(sorted(ass_norm_list))

    def match_iter(self, s_assign):
        """ iterates through all matching assignments

        Args:
            s_assign (str): input string to match to assignment

        Returns:
            s_assign_tup (tup): all matching assignments
        """
        ass_search_norm = normalize(s_assign)

        for ass in self:
            if ass_search_norm in ass:
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
