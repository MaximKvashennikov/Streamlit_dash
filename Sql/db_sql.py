import pyodbc
import pandas as pd


class ConnectSql:
    def __init__(self, database=None, request=None):
        self.connect_db = pyodbc.connect("DRIVER={SQL Server};"
                                         "SERVER=TIS-SQL-CLU-A.corp.tele2.ru;"
                                         f"Database={database};"
                                         "PORT=1433;"
                                         "UID=accessnetwork;"
                                         "PWD=xvd5c;"
                                         )
        self.request = request

    def get_cursor(self):
        return self.connect_db.cursor()

    def execute_request(self):
        return self.get_cursor().execute(self.request)


if __name__ == '__main__':
    str_sql = ("SELECT * "
               "FROM [Reports_Tele2].[dbo].[ReportWFLRRLExtend] "
               "WHERE ([TaskStatus_name] in ('Переадресованные', 'Новые', 'Поддерживаемые'))"
               "and [Ответсвенное подразделение] in ('МР', 'Р')")

    sql = ConnectSql("Reports", str_sql)

    # query = sql.execute_request()
    # query_table = query.fetchall()
    # print(query_table)

    df = pd.read_sql(str_sql, sql.connect_db)
    # df.to_excel("test.xlsx", encoding="utf-8")
    print(df)
    sql.connect_db.close()
