

from flask import render_template
# from flask import request

# import json
import os
import random

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from . import app


user = 'mikemoran'
host = 'localhost'
dbname = 'fullstations'
db = create_engine(f'postgres://{user}@{host}/{dbname}')
conn = None
conn = psycopg2.connect(database=dbname, user=user)


@app.route('/')
@app.route('/index')
def index():
    logo_file = get_random_logo()
    # lines = get_line_characters()
    details = get_stations_associated_with_lines()
    details.sort(key=lambda x: x[2])
    return render_template('index.html',
                           details=details,
                           logo_file=logo_file)


def get_random_logo():
    files = list(filter(lambda x: x.endswith('png'),
                        os.listdir(app.static_folder)))
    return random.choice(files)


def get_line_characters():
    query = '''
        select distinct linename from details;
    '''
    lines = pd.read_sql(query, conn)['linename'].tolist()
    return sorted(list(set(''.join(lines))))


def get_stations_associated_with_lines():
    query = '''
        select unit, station, linename from details;
    '''
    details = pd.read_sql(query, conn)
    units = details.unit.unique().tolist()
    stations = [details.station[details.unit == u].iloc[-1] for u in units]
    lines = [details.linename[details.unit == u].tolist() for u in units]
    lines = [''.join(sorted(list(set(''.join(l))))) for l in lines]
    return list(zip(units, stations, lines))
