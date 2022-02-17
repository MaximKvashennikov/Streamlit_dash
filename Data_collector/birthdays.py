from datetime import datetime

year = datetime.now().year
date_birthdays_dict = {
    "Малахова Ирина Васильевна": datetime.strptime(f"28-01-{year}", "%d-%m-%Y"),
    "Буянов Илья Александрович": datetime.strptime(f"08-06-{year}", "%d-%m-%Y"),
    "Ксенчук Василий Викторович": datetime.strptime(f"22-05-{year}", "%d-%m-%Y"),
    "Морозов Андрей Андреевич": datetime.strptime(f"03-02-{year}", "%d-%m-%Y"),
    "Погодин Николай Александрович": datetime.strptime(f"02-11-{year}", "%d-%m-%Y"),
    "Смирнов Александр Алексеевич": datetime.strptime(f"14-06-{year}", "%d-%m-%Y"),
    "Квашенников Максим Валерьевич": datetime.strptime(f"22-04-{year}", "%d-%m-%Y"),
    "Бугров Александр Владимирович": datetime.strptime(f"27-01-{year}", "%d-%m-%Y"),
    "Кожин Денис Николаевич": datetime.strptime(f"05-10-{year}", "%d-%m-%Y")
}


def dr():
    return [man[0] for man in date_birthdays_dict.items() if
            (man[1] - datetime.now()).days in range(-1, 8)]
