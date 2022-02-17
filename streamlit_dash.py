import streamlit as st
import pandas as pd
import os
from Sql.db_sql import ConnectSql
from Data_collector import birthdays
from Data_collector.number_week import three_week
import streamlit.components.v1 as components
import seaborn as sns
import matplotlib.pyplot as plt
from pandas import concat
from Data_collector.get_integrity import get_percentage_of_overloaded
from Data_collector.vacation import vacations_access
from Data_collector.noc import get_duty
from Data_collector.lost_of_statistics import get_df_lost_of_statistics


def det_table_sql(str_sql):
    sql = ConnectSql("Reports", str_sql)
    df_sql = pd.read_sql(str_sql, sql.connect_db)
    sql.connect_db.close()
    return df_sql


def count_week_table(df_now, df_previous, df_completed_now, df_completed_previous, now_week, previous_week):
    list_date = [
        [now_week, len(df_now.index), len(df_completed_now.index)],
        [previous_week, len(df_previous.index), len(df_completed_previous.index)]
    ]
    df_summary_table = pd.DataFrame(
        list_date,
        columns=['Номер недели', 'Количество выданных заданий', 'Количество выполненых заданий']
    )
    return df_summary_table


def count_in_work_table(df_now_in_work, df_now_in_work_mr):
    list_date = [
        [len(df_now_in_work.index), len(df_now_in_work_mr.index)]
    ]
    df_summary_table = pd.DataFrame(
        list_date,
        columns=['Количество заданий всего в работе ', 'Количество заданий в ЗО МР/Р']
    )
    return df_summary_table


def count_complete_reason_table(df_4pika, df_roll, df_150, df_mbh):
    list_date = [
        [len(df_4pika.index), len(df_roll.index), len(df_150.index), len(df_mbh.index),
         len(df_4pika.index) + len(df_roll.index) + len(df_150.index) + len(df_mbh.index)]
    ]
    df_summary_table = pd.DataFrame(
        list_date,
        columns=['4 пика', 'Rollout/Capacity', '150-200', 'MBH/резерв', 'Всего SW расширений']
    )
    return df_summary_table


if __name__ == '__main__':
    now_week = three_week()[0]
    previous_week = three_week()[1]

    vacations_list = vacations_access(os.getcwd() + "\\Data_collector\\vacation.json")
    dr_list = birthdays.dr()
    if len(dr_list) > 0:
        for man_happy in dr_list:
            st.sidebar.subheader(f"Скоро День рождения :)\n{','.join(dr_list)}")
            st.sidebar.write(birthdays.date_birthdays_dict[man_happy].strftime("%d.%m.%Y"))
    if len(vacations_list) > 0:
        st.sidebar.subheader(f"Скоро отпуск:\n{', '.join(vacations_list[0][1])}")
        st.sidebar.write(f"Неделя - w{vacations_list[0][0]}")

    options = st.sidebar.multiselect(
        'Выберите МР для поиска дежурного NOC',
        ['N-W', 'Moscow', 'South', 'Ural', 'Volga', 'F-EAST', 'CBS', 'Siberia', 'Centre'])

    st.sidebar.write(get_duty(options))

    st.subheader('Сводные данные')
    df_all_tasks_now_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {now_week} and [Name] = 'Анализ утилизации РРЛ' and [CloseCode] = 'Да')")
    )

    df_all_tasks_previous_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Анализ утилизации РРЛ' and [CloseCode] = 'Да')")
    )

    df_completed_tasks_now_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {now_week} and [Name] = 'Проконтролируй расширение'"
            f" and [CloseCode] = 'Конфигурация оборудования выполнена корректно')"
            f"UNION SELECT * FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {now_week} and [Name] = 'Выполни SW расширение РРЛ' "
            f"and [CloseCode] = 'Расширение успешно завершено')"
            f"UNION SELECT * FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {now_week} and [Name] = 'Контроль выполнения перемаршрутизации' "
            f"and [CloseCode] = 'Да')"
        )
    )

    df_completed_tasks_previous_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Проконтролируй расширение'"
            f" and [CloseCode] = 'Конфигурация оборудования выполнена корректно')"
            f"UNION SELECT * FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Выполни SW расширение РРЛ' "
            f"and [CloseCode] = 'Расширение успешно завершено')"
            f"UNION SELECT * FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Контроль выполнения перемаршрутизации' "
            f"and [CloseCode] = 'Да')"
        )
    )

    count_week_task_all = count_week_table(df_all_tasks_now_week,
                                           df_all_tasks_previous_week,
                                           df_completed_tasks_now_week,
                                           df_completed_tasks_previous_week,
                                           now_week,
                                           previous_week)
    st.dataframe(count_week_task_all)

    df_all_in_work_tasks_now_week = det_table_sql(
        ("SELECT * "
         "FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
         "WHERE ([TaskStatus_name] in ('Переадресованные', 'Новые', 'Поддерживаемые'))"
         )
    )

    df_all_in_work_tasks_mr_now_week = det_table_sql(
        ("SELECT * "
         "FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
         "WHERE ([TaskStatus_name] in ('Переадресованные', 'Новые', 'Поддерживаемые'))"
         "and [Ответсвенное подразделение] in ('МР', 'Р')"
         )
    )
    count_week_task_in_work = count_in_work_table(df_all_in_work_tasks_now_week, df_all_in_work_tasks_mr_now_week)
    st.dataframe(count_week_task_in_work)

    df_4_pika_completed_previous_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Выполни SW расширение РРЛ' "
            f"and [CloseCode] = 'Расширение успешно завершено' and [reasonOfExtending] = '4 пика')")
    )

    df_rollout_completed_previous_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Выполни SW расширение РРЛ' "
            f"and [CloseCode] = 'Расширение успешно завершено' and [reasonOfExtending] = 'RO/CAP')")
    )

    df_150_200_completed_previous_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Выполни SW расширение РРЛ' "
            f"and [CloseCode] = 'Расширение успешно завершено' and [reasonOfExtending] in ('150-200', '150M'))")
    )

    df_MBH_completed_previous_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Выполни SW расширение РРЛ' "
            f"and [CloseCode] = 'Расширение успешно завершено' and [reasonOfExtending] in ('MBH', 'резерв'))")
    )
    df_completed_reason_all_previous_week = count_complete_reason_table(
        df_4_pika_completed_previous_week,
        df_rollout_completed_previous_week,
        df_150_200_completed_previous_week,
        df_MBH_completed_previous_week
    )
    st.markdown(f'Завершенные задания на неделе {previous_week}')

    st.dataframe(df_completed_reason_all_previous_week)

    try:
        st.dataframe(get_percentage_of_overloaded())
    except ValueError:
        st.error(f'В отчете "RRL integrity Ежегодный свод" нет данных за предыдущую неделю {previous_week}')

    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: rgb(178, 208, 217);
    }
    </style>""", unsafe_allow_html=True)

    try:
        if st.button('Получить свод Lost_of_Statistics'):
            st.dataframe(get_df_lost_of_statistics())
    except PermissionError:
        st.error('Нет доступа к отчету, файл занят, попробуйте нажать еще раз')

    st.subheader('Трафик на asbr')
    components.iframe("http://10.77.252.78:88/graphs/asbr_daily_traf_big.png", width=900, height=400, scrolling=True)

    st.subheader(f'Количество заданий на w{now_week}')
    df_analyzes = det_table_sql(
        (
            "SELECT [MR], COUNT([Name]) as 'Количество задач, шт.' "
            "FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekStart] = {now_week} and [Name] = 'Анализ утилизации РРЛ') "
            "GROUP BY [MR]")
    )
    df_analyzes['Тип задачи'] = "Анализ утилизации"

    df_completed = det_table_sql(
        (
            "SELECT [MR], COUNT([Name]) as 'Количество задач, шт.' "
            "FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekStart] = {now_week} and [Name] = 'Выполни SW расширение РРЛ') "
            "GROUP BY [MR]")
    )
    df_completed['Тип задачи'] = "Выполни SW расширение РРЛ"
    df_all_week_task = concat([df_analyzes, df_completed], sort=False)

    try:
        sns.barplot(x='MR', y='Количество задач, шт.', data=df_all_week_task, ci=None, hue="Тип задачи")
        plt.xticks(rotation=90)
        st.pyplot(plt, fontsize=40)
    except:
        st.error('Проблема с отчетом "WFL расширение РРЛ подробный с фильтрами"')
