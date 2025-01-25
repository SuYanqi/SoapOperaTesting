from datetime import datetime
from datetime import timedelta
from config import DATETIME_FORMAT, COMMIT_DATETIME_FORMAT


class DatetimeUtil:

    @staticmethod
    def divide_date_by_timedelta(start_date, end_date, delta=365):
        """
        divide start_date, end_date by delta days
        return [date_0, date_1, ...]
        """
        date_list = []
        delta = timedelta(days=delta)
        start_date = datetime.strptime(start_date, DATETIME_FORMAT)
        end_date = datetime.strptime(end_date, DATETIME_FORMAT)
        while start_date < end_date:
            date_list.append(start_date.strftime(DATETIME_FORMAT))
            start_date = start_date + delta
        date_list.append(end_date.strftime(DATETIME_FORMAT))
        return date_list

    @staticmethod
    def comvert_timestamp_into_readable_format(timestamp, date_format=COMMIT_DATETIME_FORMAT):
        # Convert Unix timestamp to datetime object
        # timestamp = 1628891567
        date = datetime.utcfromtimestamp(timestamp)

        # Format datetime object
        formatted_date = date.strftime(date_format)
        return formatted_date

