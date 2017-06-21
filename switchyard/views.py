

from flask import render_template
from flask import request

# import json
import os
import random

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from . import app, model


user = 'mikemoran'
host = 'localhost'
dbname = 'fullstations'
db = create_engine(f'postgres://{user}@{host}/{dbname}')
conn = None
conn = psycopg2.connect(database=dbname, user=user)
model = model.Model(conn)

filename = f'{app.static_folder}/data/line_station_color_details.csv'
details_df = pd.read_csv(filename)


@app.route('/')
@app.route('/index')
def index():
    unit = request.args.get('unit')
    index = request.args.get('i')
    unit = 'R001' if unit is None else unit
    index = 1 if index is None else index
    model.update(unit)
    details = model.details.values.tolist()
    details.sort(key=lambda x: x[1])
    color = pull_data(unit)
    logo_file = get_random_logo()
    return render_template('index.html',
                           unit=unit,
                           index=index,
                           details=details,
                           logo_file=logo_file,
                           data=model.station_data,
                           color=color)


def pull_data(unit):
    color = details_df.color[details_df.unit == unit].values[0]
    return color


def get_random_logo():
    files = list(filter(lambda x: x.endswith('png'),
                        os.listdir(f'{app.static_folder}/images')))
    return random.choice(files)
