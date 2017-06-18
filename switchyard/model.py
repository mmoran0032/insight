

import pandas as pd


class Model:
    def __init__(self, conn):
        self.conn = conn
        self.basic = '''
            select * from {} where date_time >= '2017-01-01';
        '''

    def load_data(self, unit, daily=False):
        data = pd.read_sql(self.basic.format(unit), self.conn,
                           parse_dates=['date_time'])
        if daily:
            data['date'] = data['date_time'].dt.date
            return data.groupby('date')[['enter', 'exit']].sum().reset_index()
        return data

    def get_most_affected(self, unit):
        pass
