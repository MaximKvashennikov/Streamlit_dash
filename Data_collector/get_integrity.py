import pandas as pd
from Data_collector.number_week import three_week
from streamlit import cache


def get_integrity():
    path_integrity = "L:\Transport_planning\VISIO ЧТП\Access\Operation Group\RRL_integrity_Ежегодный свод.xlsx"

    xls = pd.ExcelFile(path_integrity)
    df = pd.read_excel(
        path_integrity,
        sheet_name=xls.sheet_names[-1],
    )

    return df


@cache(allow_output_mutation=True)
def get_percentage_of_overloaded(df):
    week_previous_integrity = f"w{three_week()[1][-2:]}"
    df = df[["Label", week_previous_integrity]].head(2)

    df[week_previous_integrity].iloc[0] = f"{round(df[week_previous_integrity].iloc[0] * 100, 3)}"
    df[week_previous_integrity].iloc[1] = f"{round(df[week_previous_integrity].iloc[1])}"
    df = df.style.set_properties(**{'background-color': '#E6E6FA',
                                    'font-size': '14pt',
                                    })
    return df
