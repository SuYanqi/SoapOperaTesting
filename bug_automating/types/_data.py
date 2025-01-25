from datetime import datetime

from config import TO_DICT_OMIT_ATTRIBUTES


class _Data:
    def __init__(self):
        pass

    def to_dict(self, seen=None):
        """
        Returns a dictionary representation of the _Data instance.
        Recursively converts nested objects to dictionaries.
        """
        if seen is None:
            seen = set()
        if id(self) in seen:
            return f"<Circular reference to {self.__class__.__name__} object>"
        seen.add(id(self))

        result = {}
        for k, v in self.__dict__.items():
            if k not in TO_DICT_OMIT_ATTRIBUTES:
                if isinstance(v, _Data):
                    result[k] = v.to_dict(seen)
                elif isinstance(v, list):
                    result[k] = [item.to_dict(seen) if isinstance(item, _Data) else item for item in v]
                elif isinstance(v, dict):
                    result[k] = {str(key): value.to_dict(seen) if isinstance(value, _Data) else value for key, value in
                                 v.items()}
                elif isinstance(v, datetime):
                    result[k] = v.isoformat()
                else:
                    result[k] = v
        return result

    # def from_dict_to_object(self, dict_data: Dict[str, Any], seen=None):
    #     """
    #     Set attributes values by the given dict_data.
    #     Recursively converts nested dictionaries to objects.
    #     Args:
    #         dict_data (dict): The dict with attributes and values.
    #     """
    #     if seen is None:
    #         seen = set()
    #     if id(self) in seen:
    #         return
    #     seen.add(id(self))
    #
    #     for key, value in dict_data.items():
    #         if hasattr(self, key):
    #             attr = getattr(self, key)
    #             if isinstance(attr, _Data):
    #                 attr.from_dict_to_object(value, seen)
    #             elif isinstance(attr, list) and value and isinstance(value[0], dict):
    #                 setattr(self, key, [self._dict_to_object(item, type(attr[0]), seen) for item in value])
    #             elif isinstance(attr, dict) and value and isinstance(list(value.values())[0], dict):
    #                 setattr(self, key,
    #                         {k: self._dict_to_object(v, type(list(attr.values())[0]), seen) for k, v in value.items()})
    #             elif isinstance(attr, datetime):
    #                 setattr(self, key, datetime.fromisoformat(value))
    #             else:
    #                 setattr(self, key, value)
    #         else:
    #             setattr(self, key, value)

    def set_attributes(self, **kwargs):
        """
        Dynamically sets attributes based on provided keyword arguments.
        Args:
            **kwargs: Key-value pairs to set as attributes.
        Raises:
            AttributeError: If a given attribute is not defined in the class.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"No attribute {key} defined in {self.__class__.__name__}.")

    # def _dict_to_object(self, data, cls, seen):
    #     if isinstance(data, dict):
    #         obj = cls()
    #         obj.from_dict(data, seen)
    #         return obj
    #     return data
