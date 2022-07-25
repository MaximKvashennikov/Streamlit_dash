from datetime import datetime, timedelta


def three_week():
    """Получение номера недели, возвращает текущую и предыдущую недели"""

    current_date = datetime.today().isocalendar()
    current_week = str(current_date[1])
    current_year = str(current_date[0])[-2:]

    previous_date = (datetime.now() - timedelta(days=7)).isocalendar()
    previous_week = str(previous_date[1])
    previous_year = str(previous_date[0])[-2:]

    next_date = (datetime.now() + timedelta(days=7)).isocalendar()
    next_week = str(next_date[1])
    next_year = str(next_date[0])[-2:]

    if len(current_week) == 1:
        current_week = f"0{current_week}"

    if len(previous_week) == 1:
        previous_week = f"0{previous_week}"

    if len(next_week) == 1:
        next_week = f"0{next_week}"

    return [current_year + current_week, previous_year + previous_week, next_year + next_week]


def months_week():
    """Получение номера недели через 1, 2, 3 месяца, возвращает соответствующие недели"""

    next_one_months = (datetime.now() + timedelta(days=30)).isocalendar()
    next_one_months_week = str(next_one_months[1])
    next_one_months_year = str(next_one_months[0])[-2:]

    next_two_months = (datetime.now() + timedelta(days=60)).isocalendar()
    next_two_months_week = str(next_two_months[1])
    next_two_months_year = str(next_two_months[0])[-2:]

    next_three_months = (datetime.now() + timedelta(days=90)).isocalendar()
    next_three_months_week = str(next_three_months[1])
    next_three_months_year = str(next_three_months[0])[-2:]

    if len(next_one_months_week) == 1:
        next_one_months_week = f"0{next_one_months_week}"

    if len(next_two_months_week) == 1:
        next_two_months_week = f"0{next_two_months_week}"

    if len(next_three_months_week) == 1:
        next_three_months_week = f"0{next_three_months_week}"

    return [next_one_months_year + next_one_months_week, next_two_months_year + next_two_months_week,
            next_three_months_year + next_three_months_week]
