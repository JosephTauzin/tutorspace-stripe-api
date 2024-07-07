import json
from repositories import FirestoreRepository
from utils import string_to_datetime


def import_db_to_firestore(filename="users.json") -> None:
    with open(filename, 'r') as file:
        list_of_records = json.load(file)

    for record, record_id in list_of_records:
        FirestoreRepository("users").create_object(record)


def crazy_method_to_parse_datetimes():
    res = FirestoreRepository("users").read_collection()

    if (not res.success):
        raise Exception(res.message)

    users = res.response_list
    fields = ["ClassDate", "NextMeetingDate", "StartTime"]
    field_array = ["HistMeetingTimes", "HistMeetingTimesEnd"]

    for user in users:
        for field in fields:
            if field in user:
                try:
                    print(f"field {field} before {user[field]}, after {string_to_datetime(user[field])}")
                    FirestoreRepository("users").update_object_by_id(user["id"], {
                        field: string_to_datetime(user[field])
                    })
                except Exception as e:
                    print(e)

        for field in field_array:
            if field in user:
                new_times_list = []

                for datestr in user[field]:
                    try:
                        new_times_list.append(string_to_datetime(datestr))
                        print(f"field {field} before {user[field]}, new_times_list {new_times_list}")
                        FirestoreRepository("users").update_object_by_id(user["id"], {
                            field: new_times_list
                        })
                    except Exception as e:
                        print(e)



def create_memberships():
    pass