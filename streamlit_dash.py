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
from Data_collector.get_integrity import (get_percentage_of_overloaded, get_annual_integrity, set_annual_integrity,
                                          get_week_integrity)
from Data_collector.vacation import vacations_access
from Data_collector.noc import get_duty
from Data_collector.lost_of_statistics import get_df_lost_of_statistics
from Data_collector.eband import instance_eband
from Data_collector.template_settings import top_five_template_settings
from Data_collector.push_sites_capacity import PushReport


def det_table_sql(str_sql):
    sql = ConnectSql("Reports", str_sql)
    df_sql = pd.read_sql(str_sql, sql.connect_db)
    sql.connect_db.close()
    return df_sql


@st.cache
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


def get_df_count_week_task_all(now_week, previous_week):
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
    return count_week_table(df_all_tasks_now_week,
                            df_all_tasks_previous_week,
                            df_completed_tasks_now_week,
                            df_completed_tasks_previous_week,
                            now_week,
                            previous_week)


@st.cache
def count_in_work_table(df_now_in_work, df_now_in_work_mr):
    list_date = [
        [len(df_now_in_work.index), len(df_now_in_work_mr.index)]
    ]
    df_summary_table = pd.DataFrame(
        list_date,
        columns=['Количество заданий всего в работе ', 'Количество заданий в ЗО МР/Р']
    )
    return df_summary_table


def get_df_count_week_task_in_work():
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
    return count_in_work_table(df_all_in_work_tasks_now_week, df_all_in_work_tasks_mr_now_week)


@st.cache
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


def get_df_completed_reason_all_previous_week():
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

    df_mbh_completed_previous_week = det_table_sql(
        (
            f"SELECT * "
            f"FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
            f"WHERE ([weekEnd] = {previous_week} and [Name] = 'Выполни SW расширение РРЛ' "
            f"and [CloseCode] = 'Расширение успешно завершено' and [reasonOfExtending] in ('MBH', 'резерв'))")
    )
    return count_complete_reason_table(
        df_4_pika_completed_previous_week,
        df_rollout_completed_previous_week,
        df_150_200_completed_previous_week,
        df_mbh_completed_previous_week)


def get_df_all_week_task():
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

    return df_all_week_task


def highlight(df):
    # df = top_five_template_settings()
    ret = pd.DataFrame("", index=df.index, columns=df.columns)
    columns_list = df.columns.tolist()
    for column in columns_list[3:]:
        ret[column].loc[df[column] > df["Target"]] = "color: red;background-color:rgb(219, 219, 219)"
    ret["Delta"].loc[df[columns_list[6]] > df[columns_list[5]]] = "color: red;background-color:rgb(219, 219, 219)"
    ret["Delta"].loc[
        df[columns_list[6]] <= df[columns_list[5]]] = "color: rgb(29, 179, 44);background-color:rgb(219, 219, 219)"

    return ret


if __name__ == '__main__':
    st.sidebar.subheader(f"Дашборд PUSHREPORTS: http://10.12.47.199:8502/")

    now_week = three_week()[0]
    previous_week = three_week()[1]

    vacations_list = vacations_access(os.getcwd() + "/Data_collector/vacation.json")
    dr_list = birthdays.dr()
    if len(dr_list) > 0:
        for man_happy in dr_list:
            st.sidebar.subheader(f"Скоро День рождения :)\n{man_happy}")
            st.sidebar.write(birthdays.date_birthdays_dict[man_happy].strftime("%d.%m.%Y"))
    if len(vacations_list) > 0:
        st.sidebar.subheader(f"Скоро отпуск:\n{', '.join(vacations_list[0][1])}")
        st.sidebar.write(f"Неделя - w{vacations_list[0][0]}")

    options = st.sidebar.multiselect(
        'Выберите МР для поиска дежурного NOC',
        ['N-W', 'Moscow', 'South', 'Ural', 'Volga', 'F-EAST', 'CBS', 'Siberia', 'Centre'])

    st.sidebar.write(get_duty(options))

    st.subheader(f'Сводные данные w{now_week}')
    st.dataframe(get_df_count_week_task_all(now_week=now_week, previous_week=previous_week))

    st.subheader(f'Количество заданий на w{now_week}')
    try:
        sns.set_palette("tab10")
        sns.set_style("dark")
        plt.subplots(figsize=(10, 5))
        sns.barplot(x='MR', y='Количество задач, шт.', data=get_df_all_week_task(), ci=None, hue="Тип задачи")
        plt.xticks(rotation=90)
        plt.grid()
        st.pyplot(plt, fontsize=40)
    except:
        st.error('Проблема с отчетом "WFL расширение РРЛ подробный с фильтрами"')

    st.markdown(f'Завершенные задания на неделе {previous_week}')
    st.dataframe(get_df_completed_reason_all_previous_week())
    st.dataframe(get_df_count_week_task_in_work())

    try:
        '''Данные RRL integrity'''
        set_annual_integrity(get_week_integrity())
    except PermissionError:
        st.error(f'Закройте отчет "RRL integrity Ежегодный свод"')
    except Exception:
        st.error(f'Для отображения попробуйте обновить страницу')
    try:
        st.table(get_percentage_of_overloaded(get_annual_integrity()))
    except ValueError:
        st.error(f'В отчете "RRL integrity Ежегодный свод" нет данных за предыдущую неделю {previous_week}')

    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: rgb(178, 208, 217);
    }
    </style>""", unsafe_allow_html=True)

    try:
        st.subheader('Получить свод Lost_of_Statistics')
        options = st.multiselect(
            'Выберите All для получения всего свода или определенные МР',
            ['All', 'N-W', 'MOSCOW', 'SOUTH', 'URAL', 'VOLGA', 'F-EAST', 'CBS', 'SIB', 'CENTER'])

        st.write(get_df_lost_of_statistics(options))
    except (PermissionError, FileNotFoundError):
        st.error('Нет доступа к отчету, файл занят, попробуйте нажать еще раз')

    if st.button('Получить данные по новым Eband'):
        instance_eband = instance_eband()
        try:
            st.dataframe((instance_eband.rename_column_name_week().astype(str)).replace(
                '[.][0]$', "", regex=True))
            st.pyplot(instance_eband.show_chart_eband(), fontsize=50)
            st.pyplot(instance_eband.show_graph_sum_built_rll(), fontsize=50)
            st.dataframe((instance_eband.get_top_five_regions().astype(str)).replace(
                '[.][0]$', "", regex=True), 2000, 10000)
        except (PermissionError, FileNotFoundError, KeyError):
            if KeyError:
                st.error('Нет данных за текущую неделю')
            else:
                st.error('Проблема с отчетом "Использование eband в новом строительстве", попробуйте обновить страницу')

    st.subheader('Трафик на asbr')
    components.iframe("http://10.77.252.78:88/graphs/asbr_daily_traf_big.png", width=900, height=400, scrolling=True)

    if st.button('Получить данные по Шаблонным параметрам'):
        try:
            st.markdown(f'Топ 5 регионов:')
            st.dataframe(
                (top_five_template_settings().style.apply(highlight, axis=None)).set_properties(
                    subset=['Label'],
                    **{'font-weight': '600'}),
                2000, 10000
            )
        except PermissionError:
            st.error('Нет доступа к отчету, файл занят, попробуйте нажать еще раз или обновите страницу')
        except FileNotFoundError:
            st.error('Файл не найден')

    st.subheader('Данные из отчетов PUSHREPORTS')
    st.markdown(f'Дашборд PUSHREPORTS: http://10.12.47.199:8502/')
    # push_reports = PushReport()
    # df_rollout = push_reports.get_report_push_capacity(path=push_reports.qet_rollout_path())
    # df_capacity = push_reports.get_report_push_capacity(path=push_reports.qet_capacity_path())
    # df_vault = push_reports.get_report_push_capacity_vault(path=push_reports.qet_capacity_path())
    #
    # ip_rollout_list = df_rollout["IP"].ffill().unique().tolist()
    # ip_rollout_list.sort(key=str, reverse=True)
    # if 0 in ip_rollout_list:
    #     ip_rollout_list.remove(0)
    #
    # st.markdown(f"{push_reports.qet_capacity_path().split('/')[-1]}, {push_reports.qet_rollout_path().split('/')[-1]}")
    # try:
    #     st.plotly_chart(push_reports.show_push_capacity(df_capacity))
    #
    #     options = st.multiselect('Выберите IP для фильтрации данных rollout', ip_rollout_list)
    #     st.plotly_chart(push_reports.show_push_rollout(df_rollout, options))
    #     st.plotly_chart(push_reports.show_push_capacity_lines(df_vault))
    # except FileNotFoundError:
    #     st.error('Нет файлов за предыдущую неделю')
