import pandas as pd
import numpy as np
import os
import zipfile
from streamlit import cache


def get_path(path_user):
    """ Получение последнего файла с пролетами из папки """

    list_files_sw = [s for s in os.listdir(path_user)
                     if os.path.isfile(os.path.join(path_user, s))]
    list_files_sw.sort(key=lambda s: os.path.getmtime(os.path.join(path_user, s)))
    path_file = path_user + "\\" + list_files_sw[-1]

    return path_file


# def unpack_file_rar():
#     """ Распаковка .rar """

#     import rarfile

#     rarfile.UNRAR_TOOL = "E:\Python\Streamlit\Data_collector\\UnRAR.exe"
#     path = get_path(path_user='L:\STAT.CP.Reports\Weekly_Template_Settings_Report')
#     dir_out = "L:\Transport_planning\VISIO ЧТП\Access\Operation Group\Шаблонные параметры РРЛ\Отчеты"
#     with rarfile.RarFile(path, "r") as rf:
#         rf.extractall(dir_out)


def unpack_file_zip():
    """ Распаковка .zip """

    path = get_path(path_user='L:\STAT.CP.Reports\Weekly_Template_Settings_Report')
    # path = "E:\Python\Streamlit\Data_collector\Template_settings_w2213.zip"
    archive = zipfile.ZipFile(path, 'r')
    return archive.open(path.split('\\')[-1].replace('zip', 'xlsx'))


def template_settings():
    pd.set_option("display.max_columns", 10)
    df = pd.read_excel(
        unpack_file_zip(),
        sheet_name="TOP 10 Errors"
    )

    for column in df.columns.tolist()[3:]:
        df[column] = df[column].map('{:.2%}'.format)

    return df


def slice_df():
    df = template_settings()
    df = (pd.concat([df.iloc[:, :3], df.iloc[:, -9:]], axis=1)).drop(np.where(df['Reg'] == "UF")[0])
    return df


def top_five_template_settings():
    df = slice_df()
    df1 = (df[df["Label"] == "Capacity Settings Errors Rate"]).head(5)
    df2 = (df[df["Label"] == "Common Settings Errors Rate"]).head(5)
    df3 = (df[df["Label"] == "Port Settings Errors Rate"]).head(5)
    df = (pd.concat([df1, df2, df3], axis=0))
    df.reset_index(drop=True, inplace=True)

    return df
