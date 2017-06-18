

from flask import render_template
from flask import request

# import json
import os
import random

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from . import app


def get_stations_associated_with_lines():
    query = '''
        select unit, station, linename from details;
    '''
    details = pd.read_sql(query, conn)
    units = details.unit.unique().tolist()
    stations = [details.station[details.unit == u].iloc[-1] for u in units]
    lines = [details.linename[details.unit == u].tolist() for u in units]
    lines = [''.join(sorted(list(set(''.join(l))))) for l in lines]
    details = list(zip(units, stations, lines))
    details.sort(key=lambda x: x[2])
    return details


user = 'mikemoran'
host = 'localhost'
dbname = 'fullstations'
db = create_engine(f'postgres://{user}@{host}/{dbname}')
conn = None
conn = psycopg2.connect(database=dbname, user=user)

details = get_stations_associated_with_lines()


@app.route('/')
@app.route('/index')
def index():
    unit = request.args.get('unit')
    index = request.args.get('i')
    unit = 'R001' if unit is None else unit
    index = 1 if index is None else index
    data = pull_data(unit)
    data_2 = pull_data('R572')
    logo_file = get_random_logo()
    return render_template('index.html',
                           unit=unit,
                           index=index,
                           details=details,
                           logo_file=logo_file,
                           data=data,
                           data_2=data_2,
                           test_data=[1, 2, 3, 4, 5])


def pull_data(unit):
    query = '''
        select * from {}
            where date_time > '2016-06-01';
    '''.format(unit)
    data = pd.read_sql(query, conn)
    return data


def get_random_logo():
    files = list(filter(lambda x: x.endswith('png'),
                        os.listdir(f'{app.static_folder}/images')))
    return random.choice(files)
