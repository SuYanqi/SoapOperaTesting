from bug_automating.types._data import _Data


class TossingPath(_Data):
    def __init__(self, product_component_pair_list=None):
        super().__init__()
        self.product_component_pair_list = product_component_pair_list
        self.length = len(product_component_pair_list)
        self.product_component_pair2idx = {p: i for i, p in enumerate(self.product_component_pair_list)}

    def __repr__(self):
        return f'{self.product_component_pair_list}'

    def __str__(self):
        return f'{self.product_component_pair_list}'

    def __eq__(self, other):
        return self.product_component_pair_list == other.product_component_pair_list

    def __hash__(self):
        # print(hash(str(self)))
        return hash(str(self))


class TossingPathFramework(_Data):
    def __init__(self, tossing_path=None, bug_id_list=None, nums=None):
        super().__init__()
        self.tossing_path = tossing_path
        self.bug_id_list = bug_id_list
        self.nums = nums

    def get_nums(self):
        self.nums = len(self.bug_id_list)
        return self.nums

    def __repr__(self):
        return f'\n\t{self.tossing_path} - {self.nums}' \
               f'\n\t\t{self.bug_id_list}'

    def __str__(self):
        return f'\n\t{self.tossing_path} - {self.nums}' \
               f'\n\t\t{self.bug_id_list}'

    def object_to_dict(self):
        pass
