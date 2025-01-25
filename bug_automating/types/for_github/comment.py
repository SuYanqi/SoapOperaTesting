class Comment:
    def __init__(self,
                 text=None,
                 creation_time=None,
                 last_change_time=None):
        self.text = text
        self.creation_time = creation_time
        self.last_change_time = last_change_time

    def __repr__(self):
        return f'{self.text} - {self.creation_time} - {self.last_change_time}'

    def __str__(self):
        return f'{self.text} - {self.creation_time} - {self.last_change_time}'

    @classmethod
    def from_dict(cls, comment_dict):
        return cls(comment_dict["body"], comment_dict["created_at"], comment_dict["updated_at"])
