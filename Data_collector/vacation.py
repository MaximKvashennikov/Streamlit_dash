import Data_collector.number_week as number_week
import json


def vacations_access(path):
    with open(path, encoding="utf8") as f:
        vacation_dict = json.load(f)
    return [(week, mans) for week, mans in vacation_dict.items() if
            week in [number_week.three_week()[0], number_week.three_week()[2]]]
