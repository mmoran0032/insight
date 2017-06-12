#!/usr/bin/env python3


import argparse
import itertools
import os

import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exits, create_database
# import psycopg2


def main(database='raw_stations', user='mikemoran'):
    include_older_data = parse_arguments()
    old_files, current_files = get_file_list()
    engine = create_new_database(database, user)
    print('loading modern files...')
    load_into_database(engine, current_files, load_modern_turnstile)
    if include_older_data:
        print('loading old files...')
        load_into_database(engine, old_files, load_old_turnstile)


def parse_arguments():
    p = argparse.ArgumentParser('combine_data -- MTA turnstile processor')
    p.add_argument('-a', '--all', action='store_true')
    return p.parse_args().all


def get_file_list():
    files = sorted(os.listdir('raw_data'))
    old_files, current_files = split_files(files)
    old_files = [f'raw_data/{f}' for f in old_files]
    current_files = [f'raw_data/{f}' for f in current_files]
    return old_files, current_files


def split_files(files):
    cutoff = 'turnstile_141018.txt'  # 2014-10-18 is first new format record
    index = files.index(cutoff)
    return files[:index], files[index:]


def create_new_database(database, user):
    engine = create_engine(f'postgres://{user}@localhost/{database}')
    if not database_exits(engine.url):
        create_database(engine.url)
    return engine


def load_into_database(engine, files, parser):
    for filename in files:
        print(filename)
        df = parser(filename)
        df.to_sql('raw', engine, if_exists='append')


def load_modern_turnstile(file):
    df = pd.read_csv(file, header=0, parse_dates=[['DATE', 'TIME']],
                     infer_datetime_format=True)
    df.columns = df.columns.str.strip().str.lower().str.replace('/', '')
    return df


def load_old_turnstile(file):
    '''adjustments required due to poor file quality'''
    column_names = ['c_a', 'unit', 'scp', 'date', 'time',
                    'desc', 'entries', 'exits']
    remainders = itertools.zip_longest(*[iter(range(3, 43))] * 5, fillvalue=0)
    column_values = [[0, 1, 2, *row] for row in remainders]
    if file != 'raw_data/turnstile_120714.txt':
        frames = [pd.read_csv(file, header=None, usecols=usecols,
                              names=column_names)
                  for usecols in column_values]
    else:
        frames = [pd.read_csv(file, header=None, usecols=usecols,
                              names=column_names, skiprows=10)
                  for usecols in column_values]
    df = pd.concat(frames, axis=0)
    return reformat_old_frame(df)


def reformat_old_frame(df):
    df['date_time'] = pd.to_datetime(
        df.date + df.time, format='%m-%d-%y%H:%M:%S')
    df.drop(['date', 'time'], axis=1, inplace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.exits = pd.to_numeric(df.exits, errors='coerce')
    return df


if __name__ == '__main__':
    main()
