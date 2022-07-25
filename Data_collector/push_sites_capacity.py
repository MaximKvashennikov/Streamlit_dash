import pandas as pd
import numpy as np
from Data_collector.number_week import three_week, months_week
import os
from datetime import datetime
from Data_collector.report_context import Report
import plotly
import plotly.subplots as sub
import plotly.graph_objects as go


class PushCapacity(Report):
    @staticmethod
    def get_report_push_capacity(path):
        return pd.read_excel(
            path,
            sheet_name="Plan_weeks",
            engine="openpyxl"
        )

    @staticmethod
    def get_report_push_capacity_vault(path):
        return pd.read_excel(
            path,
            sheet_name="Сводная таблица",
            engine="openpyxl"
        )


def qet_user_path():
    """ Получение последнего файла с пролетами из папки загрузок """

    path = '//corp.tele2.ru/Folders/PUSHREPORTS/'
    preview_week = f"{str(datetime.now().year)[-2:]}{three_week()[1][-2:]}"

    return path + f"Reports_{preview_week}" + f"/Push_sites_Capacity_w{preview_week}.xlsx"


def change_color(df, mr_reg, df_filter):
    length_first = len(df[(df[df_filter] == mr_reg) & (df["plan week"] <= int(
        three_week()[0]))])
    length_second = len(df[(df[df_filter] == mr_reg) & (df["plan week"] <= int(months_week()[0])) & (
            int(three_week()[0]) < df["plan week"])])
    length_third = len(df[(df[df_filter] == mr_reg) & (df["plan week"] <= int(months_week()[1])) & (
            int(months_week()[0]) < df["plan week"])])
    length_fourth = len(df[(df[df_filter] == mr_reg) & (df["plan week"] <= int(months_week()[2])) & (
            int(months_week()[1]) < df["plan week"])])

    return [(['#fa000067'] * length_first) + (['ffa640f2'] * length_second) + (['ffec40f2'] * length_third) + (
            ['c2ff40f2'] * length_fourth) + (['#cffcde'])]


def show_push_capacity():
    year = str(datetime.now().year)[-2:]
    start_year = int(year + "00")
    end_year = int(year + "00") + 100

    df = PushCapacity().get_report_push_capacity(path=qet_user_path())

    '''Удаляем данные из желтой зоны'''
    df = df.drop(np.where(df['status'] == "Rent")[0])

    '''Получение данных по сайтам у которых нет фактической недели постройки'''
    df_sites = df[["macroregion", "region", "site", "rfs_plan_site_w", "факт RFS"]]
    df_sites = df_sites[
        (df_sites['rfs_plan_site_w'] >= start_year) & (df_sites['rfs_plan_site_w'] < end_year)
        ].fillna(0)
    df_sites = (df_sites[(df_sites['факт RFS'] == 0)])

    df_sites = df_sites.groupby(["macroregion", "region", "rfs_plan_site_w"]).agg(
        {"site": lambda x: ", ".join(x)}).reset_index()
    df_sites = df_sites.rename(columns={'site': 'sites not built', 'rfs_plan_site_w': 'plan week'}).sort_values(
        "plan week")

    df_plan = df[["macroregion", "region", "rfs_plan_site_w"]]
    df_fact = df[["macroregion", "region", "факт RFS"]]

    df_plan = df_plan.dropna(axis='index', how='any', subset=['region'])
    df_fact = df_fact.dropna(axis='index', how='any', subset=['region'])

    df_plan = df_plan[["macroregion", "region", "rfs_plan_site_w"]].value_counts().reset_index()
    df_plan.rename(columns={0: 'Количество, шт.', 'rfs_plan_site_w': 'Site RFS'}, inplace=True)
    df_fact = df_fact[["macroregion", "region", "факт RFS"]].value_counts().reset_index()
    df_fact.rename(columns={0: 'Количество, шт.', 'факт RFS': 'Site RFS'}, inplace=True)

    df_plan = df_plan[(df_plan['Site RFS'] >= start_year) & (df_plan['Site RFS'] < end_year)].sort_values("region")
    df_fact = df_fact[(df_fact['Site RFS'] >= start_year) & (df_fact['Site RFS'] < end_year)].sort_values("region")

    df_plan["Статус"] = "План"
    df_fact["Статус"] = "Факт"

    mr_list = df_plan["macroregion"].ffill().unique().tolist()
    reg_list = df_plan["region"].ffill().unique().tolist()
    mr_list.sort()
    reg_list.sort()

    fig = sub.make_subplots(
        rows=2, cols=1,
        row_heights=[2.5, 1],
        vertical_spacing=0.18,
        specs=[[{"type": "bar"}],
               [{"type": "table"}]],
    )

    fig.add_trace(go.Table(
        header=dict(values=list(df_sites.columns),
                    line_color='white',
                    fill_color='#333',
                    font=dict(color='white', size=13),
                    align='left'),
        cells=dict(values=df_sites.transpose().values.tolist(),
                   font=dict(color='black', size=13),
                   align='left')), row=2, col=1)

    fig.add_trace(go.Bar(
        x=df_plan['Site RFS'],
        y=df_plan['Количество, шт.'],
        name=f"План - {df_plan['Количество, шт.'].sum()}",
        text=df_plan['region'],
        texttemplate="%{text}<br> %{y}шт.",
        textfont={'size': 15},
        textposition="inside",
    ), row=1, col=1
    )
    fig.add_trace(go.Bar(
        x=df_fact['Site RFS'],
        y=df_fact['Количество, шт.'],
        name=f"Факт - {df_fact['Количество, шт.'].sum()}",
        text=df_fact['region'],
        texttemplate="%{text}<br> %{y}шт.",
        textfont={'size': 15},
        textposition="inside",
    ), row=1, col=1
    )

    buttons_mr = []
    for mr in mr_list:
        buttons_mr.append(dict(method='restyle',
                               label=mr,
                               visible=True,
                               args=[
                                   {'y': [(df_plan[df_plan["macroregion"] == mr])['Количество, шт.'],
                                          (df_fact[df_fact["macroregion"] == mr])['Количество, шт.']],
                                    'x': [(df_plan[df_plan["macroregion"] == mr])['Site RFS'],
                                          (df_fact[df_fact["macroregion"] == mr])['Site RFS']],
                                    'text': [(df_plan[df_plan["macroregion"] == mr])['region'],
                                             (df_fact[df_fact["macroregion"] == mr])['region']],
                                    'name': [
                                        f"План - {(df_plan[df_plan['macroregion'] == mr])['Количество, шт.'].sum()}",
                                        f"Факт - {(df_fact[df_fact['macroregion'] == mr])['Количество, шт.'].sum()}"],
                                    'cells': dict(
                                        values=(df_sites[df_sites["macroregion"] == mr]).transpose().values.tolist(),
                                        fill=dict(color=change_color(df=df_sites, mr_reg=mr, df_filter="macroregion")),
                                        font=dict(color='black', size=12),
                                        align='left',
                                    )
                                    }
                               ],
                               )
                          )
    buttons_reg = []
    for reg in reg_list:
        buttons_reg.append(dict(method='restyle',
                                label=reg,
                                visible=True,
                                args=[
                                    {'y': [(df_plan[df_plan["region"] == reg])['Количество, шт.'],
                                           (df_fact[df_fact["region"] == reg])['Количество, шт.']],
                                     'x': [(df_plan[df_plan["region"] == reg])['Site RFS'],
                                           (df_fact[df_fact["region"] == reg])['Site RFS']],
                                     'text': [(df_plan[df_plan["region"] == reg])['region'],
                                              (df_fact[df_fact["region"] == reg])['region']],
                                     'name': [
                                         f"План - {(df_plan[df_plan['region'] == reg])['Количество, шт.'].sum()}",
                                         f"Факт - {(df_fact[df_fact['region'] == reg])['Количество, шт.'].sum()}"
                                     ],
                                     'cells': dict(
                                         values=(df_sites[df_sites["region"] == reg]).transpose().values.tolist(),
                                         fill=dict(color=change_color(df=df_sites, mr_reg=reg, df_filter="region")),
                                         font=dict(color='black', size=12),
                                         align='left')
                                     },
                                ],
                                )
                           )

    fig.update_layout(
        updatemenus=[
            {
                'buttons': buttons_mr,
                'direction': 'down',
                'showactive': True,
            },
            {
                'buttons': buttons_reg,
                'direction': 'down',
                'showactive': True,
                'y': 0.94,
            }
        ],
        title="Планируемое количество к строительству объектов sites Capacity",
        xaxis_rangeslider_visible=True,
        xaxis_rangeslider_thickness=0.07,
        xaxis_tickangle=0,
        xaxis=dict(
            title='Неделя',
            titlefont_size=17,
            tickfont_size=15,
        ),
        yaxis=dict(
            title='Количество, шт.',
            titlefont_size=17,
            tickfont_size=15,
            fixedrange=False
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        height=1000,
        width=980
    )
    '''При наведении курсора мыши'''

    fig.update_traces(hoverinfo="all", row=1, hovertemplate="region: %{text}<br>Количество: %{y}шт.<br>Неделя: %{x}")

    return fig


def show_push_capacity_lines():
    df_vault = PushCapacity().get_report_push_capacity_vault(path=qet_user_path())
    # df = PushCapacity().get_report_push_capacity(path=qet_user_path())
    # df = df.drop(np.where(df['status'] == "Rent")[0])

    reg_list = df_vault["region"].ffill().unique().tolist()
    reg_list.sort()
    reg_list.remove('NO')

    # '''Данные план rfs'''
    # df_plan_rfs = df[["region", "site", "rfs_plan_site_w"]]
    # df_plan_rfs = df_plan_rfs[
    #     (df_plan_rfs['rfs_plan_site_w'] >= start_year) & (df_plan_rfs['rfs_plan_site_w'] < end_year)
    #     ].fillna(0)
    # df_plan_rfs = df_plan_rfs.groupby(["region", "rfs_plan_site_w"])['site'].count().reset_index()
    # df_plan_rfs['Количество, шт.'] = df_plan_rfs.groupby(["region"])['site'].cumsum()
    # df_plan_rfs = df_plan_rfs.drop(columns=['site'], axis=1)

    '''Данные план rfs'''
    df_plan_rfs = df_vault[df_vault['-'] == 'plan RFS']
    df_plan_rfs = df_plan_rfs.drop(columns=['Macroregion', '-'], axis=1)
    df_plan_rfs = df_plan_rfs.rename(columns={'region': 'Week'}).set_index('Week')
    df_plan_rfs = df_plan_rfs.T

    '''Данные план rfi'''
    df_plan_rfi = df_vault[df_vault['-'] == 'plan RFI']
    df_plan_rfi = df_plan_rfi.drop(columns=['Macroregion', '-'], axis=1)
    df_plan_rfi = df_plan_rfi.rename(columns={'region': 'Week'}).set_index('Week')
    df_plan_rfi = df_plan_rfi.T

    '''Данные факт rfs'''
    df_fact_rfs = df_vault[df_vault['-'] == 'fact RFS']
    df_fact_rfs = df_fact_rfs.drop(columns=['Macroregion', '-'], axis=1)
    df_fact_rfs = df_fact_rfs.rename(columns={'region': 'Week'}).set_index('Week')
    df_fact_rfs = df_fact_rfs.T

    '''Данные факт rfi'''
    df_fact_rfi = df_vault[df_vault['-'] == 'fact RFI']
    df_fact_rfi = df_fact_rfi.drop(columns=['Macroregion', '-'], axis=1)
    df_fact_rfi = df_fact_rfi.rename(columns={'region': 'Week'}).set_index('Week')
    df_fact_rfi = df_fact_rfi.T

    '''Данные факт design'''

    df_fact_design = df_vault[df_vault['-'] == 'fact design']
    df_fact_design = df_fact_design.drop(columns=['Macroregion', '-'], axis=1)
    df_fact_design = df_fact_design.rename(columns={'region': 'Week'}).set_index('Week')
    df_fact_design = df_fact_design.T

    '''Отрисовка фигур'''
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plan_rfs.index,
                             y=df_plan_rfs['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='План RFS',
                             text='',
                             marker=dict(
                                 color='#de0000',
                                 size=2,
                                 line=dict(
                                     color='#8f0404',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_plan_rfi.index,
                             y=df_plan_rfi['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='План RFI',
                             text='',
                             marker=dict(
                                 color='#d307f2',
                                 size=2,
                                 line=dict(
                                     color='#7c048f',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_fact_rfs.index,
                             y=df_fact_rfs['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='Факт RFS',
                             text='',
                             marker=dict(
                                 color='#4a08ff',
                                 size=2,
                                 line=dict(
                                     color='#3509b0',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_fact_rfi.index,
                             y=df_fact_rfi['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='Факт RFI',
                             text='',
                             marker=dict(
                                 color='#0ce87e',
                                 size=2,
                                 line=dict(
                                     color='#0aa85c',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_fact_design.index,
                             y=df_fact_design['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='Факт design',
                             text='',
                             line=dict(
                                 color='#ff9a03',
                                 width=4,
                             ),
                             marker=dict(
                                 color='#ff9a03',
                                 size=9,
                             ),
                             )
                  )

    buttons_reg = []
    for reg in reg_list:
        buttons_reg.append(dict(method='restyle',
                                label=reg,
                                visible=True,
                                args=[
                                    {'x': [df_plan_rfs.index,
                                           df_plan_rfi.index,
                                           df_fact_rfs.index,
                                           df_fact_rfi.index,
                                           df_fact_design.index],
                                     'y': [df_plan_rfs[reg],
                                           df_plan_rfi[reg],
                                           df_fact_rfs[reg],
                                           df_fact_rfi[reg],
                                           df_fact_design[reg]],
                                     'text': [[reg] * len(df_plan_rfs),
                                              [reg] * len(df_plan_rfi),
                                              [reg] * len(df_fact_rfs),
                                              [reg] * len(df_fact_rfi),
                                              [reg] * len(df_fact_design)],
                                     'name': ['План RFS', 'План RFI', 'Факт RFS', 'Факт RFI', 'Факт design'],
                                     'visible': True,
                                     },
                                ],
                                )
                           )

    fig.update_layout(
        updatemenus=[
            {
                'buttons': buttons_reg,
                'direction': 'down',
                'showactive': True,
            }
        ],
        xaxis_tickangle=0,
        xaxis=dict(
            title='Неделя',
            titlefont_size=17,
            tickfont_size=15,
        ),
        yaxis=dict(
            title='Количество, шт.',
            titlefont_size=17,
            tickfont_size=15,
            fixedrange=False
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        hovermode="x",
        height=600,
        width=980
    )
    fig.update_traces(hoverinfo="all", hovertemplate="%{text}<br>Количество: %{y}шт.<br>Неделя: %{x}")

    return fig


if __name__ == '__main__':
    year = str(datetime.now().year)[-2:]
    start_year = int(year + "00")
    end_year = int(year + "00") + 100

    df_vault = PushCapacity().get_report_push_capacity_vault(path=qet_user_path())
    df = PushCapacity().get_report_push_capacity(path=qet_user_path())
    df = df.drop(np.where(df['status'] == "Rent")[0])

    reg_list = df_vault["region"].ffill().unique().tolist()
    reg_list.sort()
    reg_list.remove('NO')
    print(reg_list)

    mr_list = df["macroregion"].ffill().unique().tolist()
    mr_list.sort()
    print(mr_list)


    # '''Данные план rfs'''
    # df_plan_rfs = df[["region", "site", "rfs_plan_site_w"]]
    # df_plan_rfs = df_plan_rfs[
    #     (df_plan_rfs['rfs_plan_site_w'] >= start_year) & (df_plan_rfs['rfs_plan_site_w'] < end_year)
    #     ].fillna(0)
    # df_plan_rfs = df_plan_rfs.groupby(["region", "rfs_plan_site_w"])['site'].count().reset_index()
    # df_plan_rfs['Количество, шт.'] = df_plan_rfs.groupby(["region"])['site'].cumsum()
    # df_plan_rfs = df_plan_rfs.drop(columns=['site'], axis=1)

    '''Данные план rfs'''
    df_plan_rfs = df_vault[df_vault['-'] == 'plan RFS']
    df_plan_rfs = df_plan_rfs.drop(columns=['Macroregion', '-'], axis=1)
    df_plan_rfs = df_plan_rfs.rename(columns={'region': 'Week'}).set_index('Week')
    df_plan_rfs = df_plan_rfs.T
    # print(df_plan_rfs)

    '''Данные план rfi'''
    df_plan_rfi = df_vault[df_vault['-'] == 'plan RFI']
    df_plan_rfi = df_plan_rfi.drop(columns=['Macroregion', '-'], axis=1)
    df_plan_rfi = df_plan_rfi.rename(columns={'region': 'Week'}).set_index('Week')
    df_plan_rfi = df_plan_rfi.T

    '''Данные факт rfs'''
    df_fact_rfs = df_vault[df_vault['-'] == 'fact RFS']
    df_fact_rfs = df_fact_rfs.drop(columns=['Macroregion', '-'], axis=1)
    df_fact_rfs = df_fact_rfs.rename(columns={'region': 'Week'}).set_index('Week')
    df_fact_rfs = df_fact_rfs.T

    '''Данные факт rfi'''
    df_fact_rfi = df_vault[df_vault['-'] == 'fact RFI']
    df_fact_rfi = df_fact_rfi.drop(columns=['Macroregion', '-'], axis=1)
    df_fact_rfi = df_fact_rfi.rename(columns={'region': 'Week'}).set_index('Week')
    df_fact_rfi = df_fact_rfi.T

    '''Данные факт design'''

    df_fact_design = df_vault[df_vault['-'] == 'fact design']
    df_fact_design = df_fact_design.drop(columns=['Macroregion', '-'], axis=1)
    df_fact_design = df_fact_design.rename(columns={'region': 'Week'}).set_index('Week')
    df_fact_design = df_fact_design.T

    '''Отрисовка фигур'''
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plan_rfs.index,
                             y=df_plan_rfs['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='План RFS',
                             text='',
                             marker=dict(
                                 color='#de0000',
                                 size=2,
                                 line=dict(
                                     color='#8f0404',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_plan_rfi.index,
                             y=df_plan_rfi['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='План RFI',
                             text='',
                             marker=dict(
                                 color='#d307f2',
                                 size=2,
                                 line=dict(
                                     color='#7c048f',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_fact_rfs.index,
                             y=df_fact_rfs['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='Факт RFS',
                             text='',
                             marker=dict(
                                 color='#4a08ff',
                                 size=2,
                                 line=dict(
                                     color='#3509b0',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_fact_rfi.index,
                             y=df_fact_rfi['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='Факт RFI',
                             text='',
                             marker=dict(
                                 color='#0ce87e',
                                 size=2,
                                 line=dict(
                                     color='#0aa85c',
                                     width=9
                                 )
                             ),
                             )
                  )

    fig.add_trace(go.Scatter(x=df_fact_design.index,
                             y=df_fact_design['AL'],
                             visible=False,
                             mode='lines+markers',
                             name='Факт design',
                             text='',
                             line=dict(
                                 color='#ff9a03',
                                 width=4,
                             ),
                             marker=dict(
                                 color='#ff9a03',
                                 size=9,
                             ),
                             )
                  )

    buttons_reg = []
    for reg in reg_list:
        buttons_reg.append(dict(method='restyle',
                                label=reg,
                                visible=True,
                                args=[
                                    {'x': [df_plan_rfs.index,
                                           df_plan_rfi.index,
                                           df_fact_rfs.index,
                                           df_fact_rfi.index,
                                           df_fact_design.index],
                                     'y': [df_plan_rfs[reg],
                                           df_plan_rfi[reg],
                                           df_fact_rfs[reg],
                                           df_fact_rfi[reg],
                                           df_fact_design[reg]],
                                     'text': [[reg] * len(df_plan_rfs),
                                              [reg] * len(df_plan_rfi),
                                              [reg] * len(df_fact_rfs),
                                              [reg] * len(df_fact_rfi),
                                              [reg] * len(df_fact_design)],
                                     'name': ['План RFS', 'План RFI', 'Факт RFS', 'Факт RFI', 'Факт design'],
                                     'visible': True,
                                     },
                                ],
                                )
                           )

    fig.update_layout(
        updatemenus=[
            {
                'buttons': buttons_reg,
                'direction': 'down',
                'showactive': True,
            }
        ],
        xaxis_tickangle=0,
        xaxis=dict(
            title='Неделя',
            titlefont_size=17,
            tickfont_size=15,
        ),
        yaxis=dict(
            title='Количество, шт.',
            titlefont_size=17,
            tickfont_size=15,
            fixedrange=False
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        hovermode="x",
        # height=600,
        # width=980
    )
    fig.update_traces(hoverinfo="all", hovertemplate="%{text}<br>Количество: %{y}шт.<br>Неделя: %{x}")

    plotly.offline.plot(fig, filename='plot.html', auto_open=True)
