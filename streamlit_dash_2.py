import streamlit as st
import os
from Data_collector import birthdays
from Data_collector.number_week import three_week
from Data_collector.vacation import vacations_access
from Data_collector.noc import get_duty
from Data_collector.push_sites_capacity import PushReport


if __name__ == '__main__':
    st.sidebar.subheader(f"Основной дашборд: http://10.12.47.199:8501/")

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

    st.subheader('Данные из отчетов PUSHREPORTS')
    push_reports = PushReport()
    df_rollout = push_reports.get_report_push_capacity(path=push_reports.qet_rollout_path())
    df_capacity = push_reports.get_report_push_capacity(path=push_reports.qet_capacity_path())
    df_vault = push_reports.get_report_push_capacity_vault(path=push_reports.qet_capacity_path())

    ip_rollout_list = df_rollout["IP"].ffill().unique().tolist()
    ip_rollout_list.sort(key=str, reverse=True)
    if 0 in ip_rollout_list:
        ip_rollout_list.remove(0)

    st.markdown(f"{push_reports.qet_capacity_path().split('/')[-1]}, {push_reports.qet_rollout_path().split('/')[-1]}")
    try:
        st.plotly_chart(push_reports.show_push_capacity(df_capacity))

        options = st.multiselect('Выберите IP для фильтрации данных rollout', ip_rollout_list)
        st.plotly_chart(push_reports.show_push_rollout(df_rollout, options))
        st.plotly_chart(push_reports.show_push_capacity_lines(df_vault))
    except FileNotFoundError:
        st.error('Нет файлов за предыдущую неделю')
