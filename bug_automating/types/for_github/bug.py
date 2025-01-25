from datetime import datetime

from bug_finding.types.for_github.comment import Comment
from bug_finding.types.description import Description
from bug_finding.types.product_component_pair import ProductComponentPairFramework
from bug_finding.types.tossing_path import TossingPathFramework


class Bug:
    """
    from GitHub issues
    """

    def __init__(self, id=None, summary=None, description=None, creation_time=None,
                 closed_time=None, last_change_time=None, status=None, labels=None, comments=None):
        self.id = id
        self.summary = summary
        self.description = description
        self.creation_time = creation_time
        self.closed_time = closed_time
        self.last_change_time = last_change_time
        self.status = status
        self.labels = labels
        self.comments = comments

        # self.events = list()

    def __repr__(self):
        return f'ID: {self.id} - Summary: {self.summary}\n' \
               f'Description: {self.description}\n' \
               f'Created at: {self.creation_time} - Closed at: {self.closed_time} - Updated at: {self.last_change_time}\n' \
               f'Status: {self.status} - Labels: {self.labels}\n' \
               f'Comments: {self.comments}'

    def __str__(self):
        return f'ID: {self.id} - Summary: {self.summary}\n' \
               f'Description: {self.description}\n' \
               f'Created at: {self.creation_time} - Closed at: {self.closed_time} - Updated at: {self.last_change_time}\n' \
               f'Status: {self.status} - Labels: {self.labels}\n' \
               f'Comments: {self.comments}'

    @staticmethod
    def from_dict(bug_dict):
        """
        get bugs from GitHub's issues
        :param bug_dict:
        :return:
        """
        bug = Bug()
        bug.id = bug_dict['url'].replace("api.", "").replace("/repos", "")
        bug.summary = bug_dict['title']
        try:
            bug.description = Description.from_text(bug_dict['body'])
        except:
            pass
        bug.creation_time = datetime.strptime(bug_dict['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        if bug_dict['closed_at'] is not None:
            bug.closed_time = datetime.strptime(bug_dict['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
        bug.last_change_time = datetime.strptime(bug_dict['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
        bug.status = bug_dict['state']
        bug.labels = Bug.get_labels(bug_dict['labels'])
        bug.comments = Bug.get_comments(bug_dict['comments'])
        return bug

    @staticmethod
    def get_labels(labels_dict):
        labels = list()
        for label_dict in labels_dict:
            labels.append(label_dict['name'])
        return labels

    @staticmethod
    def get_comments(comments_dict):
        comments = list()
        for comment_dict in comments_dict:
            comments.append(Comment.from_commit_file_dict(comment_dict))
        return comments


class Bugs:
    def __init__(self, bugs=None):
        self.bugs = bugs
        # self.product_component_pair_framework_list = product_component_pair_framework_list
        # self.length = len(bugs)

    def __iter__(self):
        for bug in self.bugs:
            yield bug

    def get_length(self):
        return len(self.bugs)

    def get_specified_label_bugs(self, label):
        """
        get specified label's bugs from bugs
        :param label: specified label
        :return: specified label's bugs
        """
        specified_bugs = []
        for bug in self.bugs:
            if label in bug.labels:
                specified_bugs.append(bug)
        return Bugs(specified_bugs)

    # def classify_bugs_by_product_component_pair_list(self, product_component_pair_list):
    #     """
    #     使用product&component_pair_list将bugs分类
    #     :param product_component_pair_list:
    #     :return: product_component_pair - bugs dict
    #     """
    #     pc_bugs_dict = dict()
    #     for pc in product_component_pair_list:
    #         pc_bugs_dict[pc] = self.get_specified_product_component_bugs(pc)
    #
    #     return pc_bugs_dict

    # def get_pc_mistossed_bug_num(self, product_component_pair_list):
    #     """
    #     get pc: mistossed bug num dict
    #     mistossed bug: tossed out bugs
    #     :param product_component_pair_list:
    #     :return: pc: mistossed bug num dict
    #     """
    #     pc_mistossed_bug_num = dict()
    #     for bug in self.bugs:
    #         # print(f'https://bugzilla.mozilla.org/show_bug.cgi?id={bug.id}')
    #         for pc in bug.tossing_path.product_component_pair_list:
    #             if pc in product_component_pair_list and pc != bug.product_component_pair:
    #                 pc_mistossed_bug_num[f"{pc.product}::{pc.component}"] = pc_mistossed_bug_num.get(
    #                     f"{pc.product}::{pc.component}", 0) + 1
    #
    #     for pc in product_component_pair_list:
    #         if f"{pc.product}::{pc.component}" not in pc_mistossed_bug_num.keys():
    #             pc_mistossed_bug_num[f"{pc.product}::{pc.component}"] = pc_mistossed_bug_num.get(
    #                 f"{pc.product}::{pc.component}", 0)
    #     return pc_mistossed_bug_num

    # def get_pc_mistossed_bug_dict(self, product_component_pair_list):
    #     """
    #     get pc: mistossed bugs dict
    #     mistossed bug: tossed out bugs
    #     :param product_component_pair_list:
    #     :return: pc: mistossed bugs dict
    #     """
    #     pc_mistossed_bug_dict = dict()
    #     for bug in self.bugs:
    #         # print(f'https://bugzilla.mozilla.org/show_bug.cgi?id={bug.id}')
    #         for pc in bug.tossing_path.product_component_pair_list:
    #             if pc in product_component_pair_list and pc != bug.product_component_pair:
    #                 temp = pc_mistossed_bug_dict.get(pc, list())
    #                 temp.append(bug)
    #                 pc_mistossed_bug_dict[pc] = temp
    #         # print(pc_mistossed_bug_dict)
    #         # input()
    #     for pc in product_component_pair_list:
    #         if pc not in pc_mistossed_bug_dict.keys():
    #             temp = pc_mistossed_bug_dict.get(pc, list())
    #             pc_mistossed_bug_dict[pc] = temp
    #     return pc_mistossed_bug_dict

    def overall_bugs(self):
        """
        统计bugs中每个product&component包含的bug个数、tossing bug个数 及 tossing path数
        :return:
        """
        p_c_pair_list = []
        p_c_pair_framework_list = []

        for bug in self.bugs:
            # bug = Bug.dict_to_object(bug)
            if bug.product_component_pair not in p_c_pair_list:
                p_c_pair_list.append(bug.product_component_pair)

                p_c_pair_framework = ProductComponentPairFramework()
                p_c_pair_framework.product_component_pair = bug.product_component_pair
                p_c_pair_framework.bug_nums = 1

                p_c_pair_framework.tossing_path_framework_list = []
                tossing_path_framework = TossingPathFramework()
                tossing_path_framework.tossing_path = bug.tossing_path
                tossing_path_framework.nums = 1
                tossing_path_framework.bug_id_list = []
                tossing_path_framework.bug_id_list.append(bug.id)
                p_c_pair_framework.tossing_path_framework_list.append(tossing_path_framework)
                p_c_pair_framework_list.append(p_c_pair_framework)
            else:
                for framework in p_c_pair_framework_list:
                    if bug.product_component_pair == framework.product_component_pair:
                        framework.bug_nums = framework.bug_nums + 1
                        i = 0
                        for tossing_path_framework in framework.tossing_path_framework_list:
                            if tossing_path_framework.tossing_path == bug.tossing_path:
                                tossing_path_framework.bug_id_list.append(bug.id)
                                tossing_path_framework.nums = tossing_path_framework.nums + 1
                                break
                            i = i + 1
                        if i == len(framework.tossing_path_framework_list):
                            tossing_path_framework = TossingPathFramework()
                            tossing_path_framework.tossing_path = bug.tossing_path
                            tossing_path_framework.bug_id_list = []
                            tossing_path_framework.bug_id_list.append(bug.id)
                            tossing_path_framework.nums = 1
                            framework.tossing_path_framework_list.append(tossing_path_framework)
                        break
        sum = 0
        sum_tossing = 0
        sum_tossing_path = 0
        for p_c_pair_framework in p_c_pair_framework_list:
            p_c_pair_framework.get_tossing_bug_nums()
            sum = sum + p_c_pair_framework.bug_nums
            sum_tossing = sum_tossing + p_c_pair_framework.tossing_bug_nums
            sum_tossing_path = sum_tossing_path + len(p_c_pair_framework.tossing_path_framework_list)
        # overall
        print(f'bug_nums: {sum}')
        print(f'tossing_bug_nums: {sum_tossing}')  # tossing bug nums
        print(f'tossing_path_nums: {sum_tossing_path}')  # tossing path nums
        print(f'product_component_nums: {len(p_c_pair_framework_list)}')
        for p_c_pair_framework in p_c_pair_framework_list:
            print(p_c_pair_framework.product_component_pair)
            # each of p&c
            print(f'bug_nums: {p_c_pair_framework.bug_nums}')
            print(f'tossing_bug_nums: {p_c_pair_framework.tossing_bug_nums}')
            print(f'tossing_path_nums: {len(p_c_pair_framework.tossing_path_framework_list)}')
        self.product_component_pair_framework_list = p_c_pair_framework_list
        # print(self.product_component_pair_framework_list)

    # def get_bug_summary_list(self):
    #     """
    #     get bugs' summary
    #     :return: bug summary list
    #     """
    #     summary_list = []
    #     for bug in self.bugs:
    #         id_summary = {"id": f'https://bugzilla.mozilla.org/show_bug.cgi?id={bug.id}',
    #                       "summary": bug.summary}
    #         summary_list.append(id_summary)
    #     return summary_list

    def sort_by_creation_time(self):
        self.bugs = sorted(self.bugs, key=lambda x: x.creation_time, reverse=False)

    def split_dataset_by_creation_time(self):
        """
        sort bugs by creation time
        split bugs into
            80% training dataset
            20% testing dataset
        :return:
        """
        self.sort_by_creation_time()

        train_bugs = list()
        test_bugs = list()
        i = 0
        for bug in self.bugs:
            if i < 0.8 * self.get_length():
                train_bugs.append(bug)
            else:
                test_bugs.append(bug)
            i = i + 1
        train_bugs = Bugs(train_bugs)
        # train_bugs.overall_bugs()
        test_bugs = Bugs(test_bugs)
        # test_bugs.overall_bugs()
        return train_bugs, test_bugs

    # def split_dataset_by_pc(self, product_component_pair_list):
    #     """
    #     split bugs according to pc, for each pc: 80% training dataset & 20% testing dataset
    #     :param product_component_pair_list:
    #     :return:
    #     """
    #     train_bugs = list()
    #     test_bugs = list()
    #
    #     for pc in product_component_pair_list:
    #         bugs = self.get_specified_product_component_bugs(pc)
    #         train_bugs.extend(list(bugs)[0: int(bugs.get_length() * 0.8)])
    #         test_bugs.extend(list(bugs)[int(bugs.get_length() * 0.8): bugs.get_length()])
    #     train_bugs = Bugs(train_bugs)
    #     # train_bugs.overall_bugs()
    #     test_bugs = Bugs(test_bugs)
    #     # test_bugs.overall_bugs()
    #     return train_bugs, test_bugs

    # def split_dataset_by_pc_and_creation_time(self, product_component_pair_list):
    #     """
    #     sort bugs by creation time
    #     split bugs according to pc, for each pc: 80% training dataset & 20% testing dataset
    #     :param product_component_pair_list:
    #     :return:
    #     """
    #     self.sort_by_creation_time()
    #
    #     train_bugs = list()
    #     test_bugs = list()
    #
    #     for pc in product_component_pair_list:
    #         bugs = self.get_specified_product_component_bugs(pc)
    #         train_bugs.extend(list(bugs)[0: int(bugs.get_length() * 0.8)])
    #         test_bugs.extend(list(bugs)[int(bugs.get_length() * 0.8): bugs.get_length()])
    #     train_bugs = Bugs(train_bugs)
    #     # train_bugs.overall_bugs()
    #     test_bugs = Bugs(test_bugs)
    #     # test_bugs.overall_bugs()
    #     return train_bugs, test_bugs
