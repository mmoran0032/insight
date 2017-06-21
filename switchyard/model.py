

import pandas as pd

from . import app


class Model:
    def __init__(self):
        self.data_directory = f'{app.static_folder}/data'
        self.ridership = pd.read_csv(
            f'{self.data_directory}/ridership_since_dec.csv')
        self.ridership.set_index('date', inplace=True)
        self.ridership.columns = self.ridership.columns.str.upper()
        self.ratios = pd.read_csv(
            f'{self.data_directory}/ratio.csv')
        self.ratios.set_index('unit', inplace=True)
        self.details = pd.read_csv(
            f'{self.data_directory}/line_station_color_details.csv')
        self.station_data = None
        self.affected_station_data = None

    def update(self, unit):
        self.station_data = self.get_main_station(unit)
        affected = self.get_most_affected(unit)
        affected_riders = [self.get_affected_station(u, d)
                           for u, d in zip(affected.index, affected.values)]
        self.affected_station_data = affected_riders

    def get_main_station(self, unit):
        return self.ridership.loc[:'2017-04-30', unit]

    def get_affected_station(self, unit, delta):
        riders = self.ridership[unit]
        pre = riders.loc[:'2017-04-30']
        post = riders.loc['2017-05-01':].add(
            -delta, fill_value=1)
        riders = pd.concat([pre, post], axis=0)
        return riders

    def get_most_affected(self, unit, number=4):
        effect = self.ratios[unit]
        station_riders = self.ridership[unit]
        mean_riders = station_riders.mean()
        delta_others = 1 / (effect / mean_riders)
        count = delta_others.notnull().sum()
        return delta_others.sort_values().iloc[:number] / count

    def get_color(self, unit):
        sub_details = self.details[self.details.unit == unit]
        return sub_details['color'].iloc[0]
