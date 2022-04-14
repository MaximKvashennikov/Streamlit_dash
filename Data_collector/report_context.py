import pandas as pd
from Data_collector.number_week import three_week
from datetime import datetime
import matplotlib.pyplot as plt


class Report:
    def now_rename_week(self):
        return f"{datetime.now().year}W{three_week()[0][-2:]}"

    def preview_rename_week(self):
        return f"{datetime.now().year}W{three_week()[1][-2:]}"