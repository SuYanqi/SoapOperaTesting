def custom_sort_bug_count_dict_by_count_creation_time(item):
    return item[1], item[0].creation_time


class DictUtil:

    @staticmethod
    def sort_bug_count_dict_by_count_creation_time(my_dict, key=custom_sort_bug_count_dict_by_count_creation_time, reverse=True):
        sorted_dict = dict(sorted(my_dict.items(), key=key, reverse=reverse))
        return sorted_dict

    @staticmethod
    def to_dict(one_object):
        """
        Returns a dictionary representation of the AutonomicTask instance.
        """
        return {k: v for k, v in one_object.__dict__.items()}

    @staticmethod
    def from_dict(one_dict):
        """
        Set attributes values by the given dict_obj
        Args:
            one_dict (dict): The dict with attributes and values
        """
        for key, value in one_dict.items():
            if hasattr(one_dict, key):
                setattr(one_dict, key, value)
