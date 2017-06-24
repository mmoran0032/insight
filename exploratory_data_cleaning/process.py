

import os
import sys

import pandas as pd


def main(station, line):
    name = '_'.join(f'{station} {line}'.split()).replace('/', '_')
    print(name)
    single_station = save_station_info(station, line)
    frames = create_passenger_diffs(single_station)
    daily = get_daily_ridership(frames)
    daily['station'] = station
    daily['line'] = line

    # limit to just Jan 1 2015
    daily = daily.loc[daily.index >= '2015-01-01 00:00:00']
    daily.to_csv(f'{name}.csv')
    return daily


def read_turnstiles(filename):
    df = pd.read_csv(filename, header=0)
    df.columns = df.columns.str.strip().str.lower()
    df['datetime'] = pd.to_datetime(
        df.date + df.time, format='%m/%d/%Y%H:%M:%S')
    df.drop(['division', 'desc'], axis=1, inplace=True)
    return df


def save_station_info(station_name, line):
    frames = []
    files = [f'modern/{f}' for f in sorted(os.listdir('modern'))]

    for file in files:
        df = read_turnstiles(file)
        penn = df[(df.station == station_name) &
                  (df.linename == line)]
        penn.set_index(['datetime'], inplace=True)
        frames.append(penn)

    return pd.concat(frames, axis=0)


def create_passenger_diffs(single_station):
    frames = []
    for unit in single_station.unit.unique():
        scps = single_station[single_station.unit == unit].scp.unique()
        for scp in scps:
            frame = single_station[(single_station.unit == unit) &
                                   (single_station.scp == scp)]
            diffs = frame[['entries', 'exits']].diff()
            diffs.columns = ['d_entries', 'd_exits']
            frame = pd.concat([frame, diffs], axis=1)
            frame.drop(['entries', 'exits'], axis=1, inplace=True)
            frame.dropna(inplace=True)
            frames.append(frame)
    return frames


def get_daily_ridership(frames):
    diff_station = pd.concat(frames, axis=0)
    diff_station.reset_index(inplace=True)
    diff_station.date = pd.to_datetime(diff_station.date, format='%m/%d/%Y')
    by_day = diff_station.groupby('date').sum()
    return by_day[((by_day.d_entries < 1e6) & (by_day.d_exits < 1e6)) &
                  ((by_day.d_entries > 0) & (by_day.d_exits > 0))]


if __name__ == '__main__':
    station, line = sys.argv[1:]
    main(station, line)
