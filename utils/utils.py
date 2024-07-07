from typing import List
from datetime import datetime, timedelta
from entities import TutorPayout


def cents_to_dollars(cents: int) -> float:
    """
        Convert cents to dollars.
        Param:
            - cents(int): amount in cents
        Return:
            - float: amount in dollars
    """
    return round(cents / 100.0, 2)


def dollars_to_cents(dollars) -> int:
    """
        Convert dollars to cents.

        Params:
            - dollars: Amount in dollars
        Return:
            - int: amount in cents
    """
    return int(dollars * 100)


def calculate_hours_spent_by_range2(
        activity_starts: List[datetime],
        activity_ends: List[datetime],
        start_range: datetime,
        end_range: datetime
) -> float:
    total_hours = 0.0

    for start, end in zip(activity_starts, activity_ends):
        overlap_start = max(start, start_range)
        overlap_end = min(end, end_range)

        if (overlap_end > overlap_start):
            overlap_duration = overlap_end - overlap_start
            total_hours += overlap_duration.total_seconds() / 3600

    return total_hours


def calculate_hours_spent_by_range(
        activity_starts: List[datetime],
        activity_ends: List[datetime],
        start_range: datetime,
        end_range: datetime
) -> float:
    total_hours = 0.0

    for start, end in zip(activity_starts, activity_ends):
        if start > end:
            continue  # Skip invalid intervals where start is after end

        overlap_start = max(start, start_range)
        overlap_end = min(end, end_range)

        if overlap_end > overlap_start:
            overlap_duration = overlap_end - overlap_start
            total_hours += overlap_duration.total_seconds() / 3600

    return total_hours


def firebase_to_datetime(firebase_timestamp):
    dt = datetime.utcfromtimestamp(firebase_timestamp.second)
    dt = dt + timedelta(microseconds=firebase_timestamp.nanosecond / 1000)
    return dt


def calculate_hours_spent(
        activity_starts: List[datetime],
        activity_ends: List[datetime]
) -> float:
    total_hours = 0.0

    for start, end in zip(activity_starts, activity_ends):
        if end > start:
            time_spent = end - start
            total_hours += time_spent.total_seconds() / 3600

    return total_hours


def string_to_datetime(date_string: str) -> datetime:
    #date_string_format = "%Y-%m-%d %H:%M:%S%z"
    return datetime.fromisoformat(date_string)


begin_dates = [datetime(2023, 6, 1, 5, 0), datetime(2023, 6, 2, 12, 0)]
end_dates = [datetime(2023, 6, 1, 10, 0), datetime(2023, 6, 2, 15, 0)]

custom_start = datetime(2023, 6, 1, 0, 0)
custom_end = datetime(2023, 6, 3, 0, 0)


#total_hours = calculate_hours_spent(begin_dates, end_dates, custom_start, custom_end)
#print(f"Total hours spent in the custom range: {total_hours}")
def find_student_debt_by_student_id(data_list: list, student_id: str):
    for item in data_list:
        if item.student_id == student_id:
            return item
    return None


def find_tutor_pay_by_tutor_id(data_list: list, tutor_id: str):
    for item in data_list:
        if item.tutor_id == tutor_id:
            return item
    return None


def check_duplicated_tutor_hours(tutors_list: list) -> list:
    consolidated = {}

    for tutor in tutors_list:
        tutor: TutorPayout = tutor

        if tutor.tutor_id in consolidated:
            consolidated[tutor.tutor_id]["tutor_total_hours"] += tutor.tutor_total_hours
            consolidated[tutor.tutor_id]["tutor_payout"] += tutor.tutor_payout
        else:
            consolidated[tutor.tutor_id] = tutor.model_dump()
            consolidated[tutor.tutor_id]["tutor_total_hours"] = tutor.tutor_total_hours
            consolidated[tutor.tutor_id]["tutor_payout"] = tutor.tutor_payout

    return [TutorPayout(**tutor_parsed) for _id, tutor_parsed in consolidated.items()]
