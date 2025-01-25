from functools import reduce

from bug_automating.pipelines.placeholder import Placeholder


class ListUtil:
    @staticmethod
    def list_of_groups(init_list, children_list_len):
        """
        split list by children_list_len
        @param init_list:
        @type init_list:
        @param children_list_len:
        @type children_list_len:
        @return:
        @rtype:
        """
        list_of_groups = zip(*(iter(init_list),) * children_list_len)
        end_list = [list(i) for i in list_of_groups]
        count = len(init_list) % children_list_len
        end_list.append(init_list[-count:]) if count != 0 else end_list
        return end_list

    @staticmethod
    def convert_nested_list_to_flatten_list(nested_list):
        """
        nested_list = [[14], [215, 383, 87], [298], [374], [2, 3, 4, 5, 6, 7]]
        flatten_list = [14, 215, 383, 87, 298, 374, 2, 3, 4, 5, 6, 7]
        @param nested_list:
        @type nested_list:
        @return:
        @rtype:
        """
        flatten_list = reduce(lambda x, y: x + y, nested_list)
        return flatten_list

    @staticmethod
    def merge_sets_with_intersection_in_list(bondlist):
        """
        python 多层列表 合并有相同数值的元素
        问题描述：假如有一个列表，列表中有许多集合，集合之间可能有重复的元素，设计一个算法，将有相同元素的集合进行合并, # 并且保留值相同的重复元素。
        问题实际应用场景：成对信息在分组后需要保留的情况。
        如不需保留，将分组后用sorted函数合并相同元素
        ————————————————
        版权声明：本文为CSDN博主「YnagShanwen」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
        原文链接：https://blog.csdn.net/YnagShanwen/article/details/111344386
        @param bondlist:
        @type bondlist:
        @return:
        @rtype:
        """
        groups = []
        break1 = False
        while bondlist:
            pair1 = bondlist.pop(0)
            pair1 = list(pair1)
            b = len(pair1)
            a = b + 1  # 判断是否循环的初始值
            while b != a:
                a = b
                for atomid in pair1:
                    for i, pair2 in enumerate(bondlist):
                        if atomid in pair2:
                            pair1 = pair1 + list(pair2)
                            bondlist.pop(i)
                            if not bondlist:
                                break1 = True
                            break
                    if break1:
                        break
                b = len(pair1)
                # print(pair1)  # 测试分类过程和结果用
                # print(b)  # 测试分类过程和结果用
            groups.append(set(pair1))
        return groups

    @staticmethod
    def convert_flatten_list_to_nested_list_by_value(flatten_list, value):
        """
        value = 'c'
        Note that delete value
        @param flatten_list: ['a', 'c', ' d', ' e', 'c', 'f', 'g']
        @type flatten_list: list
        @return: [['a'], [' d', ' e'], ['f', 'g']]
        @rtype: list
        """
        sub_list = []
        nested_list = []
        for e in flatten_list:
            if e == value:
                if sub_list:
                    nested_list.append(sub_list)
                sub_list = []
            else:
                sub_list.append(e)
        nested_list.append(sub_list)
        return nested_list

    @staticmethod
    def remove_dict_by_id(list_of_dicts, key_to_remove, key='id'):
        for item in list_of_dicts:
            if item[key] == key_to_remove:
                list_of_dicts.remove(item)
                break  # Stop iteration after first match if IDs are unique

    @staticmethod
    def get_diff_by_key_from_two_dict_list(dict_list1, dict_list2, field=Placeholder.SUMMARY):
        try:
            # Convert lists to dictionaries with 'id' as the key
            dict1 = {d[field]: d for d in dict_list1}
            dict2 = {d[field]: d for d in dict_list2}

            # Find differences
            only_in_list1 = [dict1[k] for k in dict1 if k not in dict2]
            only_in_list2 = [dict2[k] for k in dict2 if k not in dict1]

            print("Items in list1 but not in list2:", only_in_list1)
            print("Items in list2 but not in list1:", only_in_list2)
            return only_in_list1, only_in_list2
        except Exception as e:
            print(e)
            # pass return dict_list1, dict_list2
