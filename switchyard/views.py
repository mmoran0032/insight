

from flask import render_template
from flask import request

# import json
import os
import random

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from . import app, model


def get_stations_associated_with_lines(conn):
    query = '''
        select unit, station, linename from details;
    '''
    details = pd.read_sql(query, conn)
    units = details.unit.unique().tolist()
    stations = [details.station[details.unit == u].iloc[-1] for u in units]
    lines = [details.linename[details.unit == u].tolist() for u in units]
    lines = [''.join(sorted(list(set(''.join(l))))) for l in lines]
    details = list(zip(units, stations, lines))
    details.sort(key=lambda x: x[1])
    return details


user = 'mikemoran'
host = 'localhost'
dbname = 'fullstations'
db = create_engine(f'postgres://{user}@{host}/{dbname}')
conn = None
conn = psycopg2.connect(database=dbname, user=user)
model = model.Model(conn)

details = get_stations_associated_with_lines(conn)
filename = f'{app.static_folder}/data/line_station_color_details.csv'
details_df = pd.read_csv(filename).set_index('unit')


@app.route('/')
@app.route('/index')
def index():
    unit = request.args.get('unit')
    index = request.args.get('i')
    unit = 'R001' if unit is None else unit
    index = 1 if index is None else index
    data, color = pull_data(unit)
    logo_file = get_random_logo()
    return render_template('index.html',
                           unit=unit,
                           index=index,
                           details=details,
                           logo_file=logo_file,
                           data=data,
                           color=color)


def pull_data(unit):
    data = model.load_data(unit, True)
    print(data.head())
    color = details_df.loc[unit, 'color']
    return data, color


def get_random_logo():
    files = list(filter(lambda x: x.endswith('png'),
                        os.listdir(f'{app.static_folder}/images')))
    return random.choice(files)
