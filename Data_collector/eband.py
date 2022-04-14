import pandas as pd
import matplotlib.pyplot as plt
from Data_collector.report_context import Report


class Eband(Report):
    def __init__(self, get_report_eband, get_summary_eband):
        self.get_report_eband = get_report_eband
        self.get_summary_eband = get_summary_eband

    def get_russia_stat(self):
        df = (self.get_report_eband.iloc[:5, 1:]).drop(self.now_rename_week(), axis=1)
        df = pd.concat([df.iloc[:, :2], df.iloc[:, -6:]], axis=1)
        df.rename(columns={'Unnamed: 2': 'Band', 'MR': ''}, inplace=True)
        df = df.fillna("")
        return df

    def rename_column_name_week(self):
        df = self.get_russia_stat()
        df.rename(columns=lambda x: f"W{x[2:4]}{x[-2:]}" if 'W' in x else x, inplace=True)
        return df

    def get_russia_stat_all_week(self):
        df = (self.get_report_eband.iloc[:5, 1:]).drop(self.now_rename_week(), axis=1)
        df = pd.concat([df.iloc[:, :2], df.iloc[:, 3:-1]], axis=1)
        df.rename(columns={'Unnamed: 2': 'Band', 'MR': ''}, inplace=True)
        df = df.fillna("")
        return df

    def get_top_five_regions(self):
        """Делаем свод топ 5 по количеству построенных БС"""

        preview__week = self.preview_rename_week()
        new_preview_week = f'W{preview__week[2:4]}{preview__week[-2:]}'

        df_summary = self.get_summary_eband[['Регион', 'Unnamed: 3', f'{preview__week}']]
        df_summary.rename(
            columns={'Unnamed: 3': '',
                     f'{preview__week}': new_preview_week},
            inplace=True
        )
        df_summary['Регион'].fillna(method='pad', inplace=True)
        df_summary.fillna(0, inplace=True)

        df_top_regions = (df_summary[df_summary[""] == "Всего"]).sort_values(by=f"{new_preview_week}",
                                                                             ascending=False).head(5)

        top_regions_list = df_top_regions['Регион'].values

        '''Фильтруем согласно списку'''
        df_top_regions = df_summary[df_summary["Регион"].str.contains('|'.join(top_regions_list))].reset_index(
            drop=True)

        '''Фильтруем по возрастанию поля "Всего"'''
        df_sort_top_regions = pd.DataFrame()
        for region in top_regions_list[::-1]:
            df_temp = df_top_regions[df_top_regions["Регион"] == region]
            df_sort_top_regions = pd.concat([
                df_temp,
                df_sort_top_regions
            ], ignore_index=True)

        df_sort_top_regions.loc[(df_sort_top_regions.index % 5 != 0), 'Регион'] = ''

        return df_sort_top_regions

    def get_built_rll(self):
        df = (self.get_report_eband.iloc[:5, 1:]).drop(self.now_rename_week(), axis=1)
        df = (pd.concat([df.iloc[:, 1:2], df.iloc[:, 3:-1]], axis=1)).loc[[1, 4]]
        df.rename(columns={'Unnamed: 2': ''}, inplace=True)
        df.fillna(0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df

    @staticmethod
    def modify_list(old_list):
        new_list = []
        first_element = 0
        for element in old_list:
            first_element += element
            new_list.append(first_element)
        return new_list

    def get_sum_built_rll(self):
        df_built = self.get_built_rll()

        sum_eband_list = self.modify_list(old_list=(df_built.loc[0].tolist())[1:])
        sum_all_list = self.modify_list(old_list=(df_built.loc[1].tolist())[1:])

        list_date = [sum_eband_list, sum_all_list]
        df = pd.DataFrame(
            list_date,
            columns=df_built.columns.tolist()[1:]
        )
        df.rename(columns=lambda x: f"W{x[2:4]}{x[-2:]}" if 'W' in x else x, inplace=True)

        return df

    def show_graph_sum_built_rll(self):
        df = self.get_sum_built_rll()
        df = df.T
        df.rename(columns={0: 'eBand', 1: 'Всего'},
                  inplace=True)

        df.plot(kind="bar", figsize=(10, 5))
        plt.ylabel("Количество, шт.")

        ax2 = plt.twinx()
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("% eBand")
        df['% eBand'] = round((df['eBand'] / df['Всего']) * 100, 1)
        ax2.plot(df['% eBand'], label='% eBand', linewidth=2, color='#1a90b8')
        ax2.legend()
        plt.grid()
        plt.title('Понедельное соотношение построенных E-Band от всех РРЛ накопительным итогом')

        return plt

    def show_chart_eband(self):
        rep_chars = 'nan|''|""|'
        df_russia_stat_all_week = self.get_russia_stat_all_week().replace(rep_chars, 0, regex=True)
        df_russia_stat_all_week.rename(columns=lambda x: f"W{x[2:4]}{x[-2:]}" if 'W' in x else x, inplace=True)

        df_new_eband = df_russia_stat_all_week.iloc[:, 1:]
        df_new_eband = df_new_eband.T.iloc[1:, :]

        df_new_eband.rename(columns={0: '% eBand', 1: 'eBand', 2: 'nBand 1,5км', 3: 'nBand 3,5км', 4: 'Всего'},
                            inplace=True)
        percent_eband = df_new_eband['% eBand']
        df_new_eband.drop(columns=["% eBand"], axis=1, inplace=True)

        df_new_eband.plot(kind="bar", figsize=(10, 5))
        plt.ylabel("Количество, шт.")
        ax2 = plt.twinx()
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("% eBand")
        ax2.plot(percent_eband, label='% eBand')
        ax2.legend()
        plt.grid()

        return plt
