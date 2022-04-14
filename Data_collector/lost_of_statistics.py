import os
import pandas as pd


def qet_user_path():
    """ Получение последнего файла с пролетами из папки загрузок """

    path_user = '//t2ru//CPFolders//T2CP-FPS-02//Transport_Network//ACCESS//Контроль дисконнектов'

    list_files_sw = [s for s in os.listdir(path_user)
                     if os.path.isfile(os.path.join(path_user, s))]
    list_files_sw.sort(key=lambda s: os.path.getmtime(os.path.join(path_user, s)))
    path_file = path_user + "\\" + list_files_sw[-1]

    return path_file


def get_df_lost_of_statistics(mr):
    df = pd.read_excel(
        qet_user_path(),
        sheet_name='Итого disconnect',
        skiprows=2,
    )
    df.drop(columns=['Unnamed: 0'], axis=1, inplace=True)
    df.rename(
        columns={f'Количество по полю _x000D_\n Network Element': 'Количество Network Element'},
        inplace=True
    )
    if "All" not in mr:
        df = df[df["Макрорегион"].str.contains('|'.join(mr))].reset_index(drop=True)
    if not mr:
        df = ""
    return df
