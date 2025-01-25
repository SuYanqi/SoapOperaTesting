from bug_automating.types._data import _Data


class ProductComponentPair(_Data):

    def __init__(self, product=None, component=None, description=None):
        super().__init__()
        self.product = product
        self.component = component
        self.description = description
        # self.community = community

    def __eq__(self, other):
        return self.product == other.product and self.component == other.component

    def __lt__(self, other):
        return f"{self.product}::{self.component}" < f"{other.product}::{other.component}"

    # def __gt__(self, other):
    #     return self.product > other.product
    #     # return self.product > other.product and self.component > other.component

    def __repr__(self):
        return f'{self.product}::{self.component}'  # - {self.community}'

    def __str__(self):
        return f'{self.product}::{self.component}'  # - {self.community}'

    def __hash__(self):
        # print(hash(str(self)))
        return hash(str(self))


class ProductComponentPairFramework(_Data):
    def __init__(self, product_component_pair=None, topic=None, bug_nums=None, tossing_bug_nums=0,
                 tossing_path_framework_list=None):
        super().__init__()
        self.product_component_pair = product_component_pair
        self.topic = topic
        self.bug_nums = bug_nums
        self.tossing_bug_nums = tossing_bug_nums
        self.tossing_path_framework_list = tossing_path_framework_list

    def get_tossing_bug_nums(self):
        flag = False
        for tossing_path_framework in self.tossing_path_framework_list:
            if tossing_path_framework.tossing_path.length == 1:
                self.tossing_bug_nums = self.bug_nums - tossing_path_framework.nums
                flag = True
                break
        if not flag:
            self.tossing_bug_nums = self.bug_nums
        return self.tossing_bug_nums

    def __repr__(self):
        return f'\n{self.product_component_pair} - {self.bug_nums} - {self.tossing_bug_nums}' \
               f'\n\t{self.tossing_path_framework_list}'

    def __str__(self):
        return f'\n{self.product_component_pair} - {self.bug_nums} - {self.tossing_bug_nums}' \
               f'\n\t{self.tossing_path_framework_list}'


class ProductComponentPairs(_Data):
    def __init__(self, product_component_pair_list=None):
        super().__init__()
        self.product_component_pair_list = product_component_pair_list

    def __repr__(self):
        return f'{self.product_component_pair_list}'

    def __str__(self):
        return f'{self.product_component_pair_list}'

    def __iter__(self):
        for pc in self.product_component_pair_list:
            yield pc

    def get_length(self):
        return len(self.product_component_pair_list)

    def get_product_component_pair_name_index_dict(self):
        pc_index_dict = dict()
        for index, pc in enumerate(self.product_component_pair_list):
            pc = f"{pc.product}::{pc.component}"
            pc_index_dict[pc] = pc_index_dict.get(pc, index)
        return pc_index_dict

    def get_product_component_pair_name_list(self):
        pc_name_list = list()
        for pc in self.product_component_pair_list:
            pc_name_list.append(f'{pc.product}::{pc.component}')
        return pc_name_list

