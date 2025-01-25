from bug_automating.types._data import _Data


class Relation(_Data):
    """
    Bug Report Relation:
        Blocks: This bug must be resolved before the bugs listed in this field can be resolved.
        Depends on: The bugs listed here must be resolved before this bug can be resolved.
        Duplicates: List of bugs that have been marked a duplicate of the bug currently being viewed.
        Regressed by: This bug has been introduced by the bugs listed here.
        Regressions: This bug has introduced the bugs listed here.
        See Also: This allows you to refer to bugs in other bug tracker installations.
                  You can enter a URL to a bug in the 'Add Bug URLs' field to note that that bug is related to this one.
                  You can enter multiple URLs at once by separating them with a comma.
                  You should normally use this field to refer to bugs in other bug tracker installations, or bugs which are related to, but not known to be duplicates of the bug.
                  Bugs which are regressions should be listed in the Regressed by field (above)
    """

    def __init__(self, bug_id, regressed_by=None, regressions=None, blocks=None, depends_on=None, duplicates=None,
                 see_also=None):
        # bug report relation
        super().__init__()
        self.bug_id = bug_id
        self.regressed_by = regressed_by
        self.regressions = regressions
        self.blocks = blocks
        self.depends_on = depends_on
        self.duplicates = duplicates
        self.see_also = see_also

    def __repr__(self):
        return f'{self.bug_id}:' \
               f'\n\tregressed_by: {self.regressed_by}' \
               f'\n\tregressions: {self.regressions}' \
               f'\n\tblocks: {self.blocks}' \
               f'\n\tdepends_on: {self.depends_on}' \
               f'\n\tduplicates: {self.duplicates}' \
               f'\n\tsee_also: {self.see_also}'

    def __str__(self):
        return f'{self.bug_id}:' \
               f'\n\tregressed_by: {self.regressed_by}' \
               f'\n\tregressions: {self.regressions}' \
               f'\n\tblocks: {self.blocks}' \
               f'\n\tdepends_on: {self.depends_on}' \
               f'\n\tduplicates: {self.duplicates}' \
               f'\n\tsee_also: {self.see_also}'

    # def __eq__(self, other):
    #     return self.text == other.text \
    # and self.id == other.id

    def __hash__(self):
        # print(hash(str(self)))
        return hash(str(self))

    @classmethod
    def from_dict(cls, bug_dict):
        # print(type(bug_dict['regressed_by']))
        regressed_by, regressions, blocks, depends_on, duplicates, see_also = [None] * 6
        if bug_dict['regressed_by']:
            regressed_by = bug_dict['regressed_by']
            # print(bug.regressed_by)
            # print(type(bug.regressed_by))
        if bug_dict['regressions']:
            regressions = bug_dict['regressions']
            # print(bug.regressions)
            # print(type(bug.regressions))
        if bug_dict['blocks']:
            blocks = bug_dict['blocks']
        if bug_dict['depends_on']:
            depends_on = bug_dict['depends_on']
        if bug_dict['duplicates']:
            duplicates = bug_dict['duplicates']
        if bug_dict['see_also']:
            see_also = bug_dict['see_also']
        return cls(bug_dict['id'], regressed_by, regressions,
                   blocks, depends_on,
                   duplicates, see_also)
