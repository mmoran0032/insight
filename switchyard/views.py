

from flask import render_template
from flask import request

# import json
import os
import random

from . import app, model


model = model.Model()


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
    color = model.get_color(unit)
    affected = condense_affected_data()
    logo_file = get_random_logo()
    return render_template('index.html',
                           unit=unit,
                           index=index,
                           details=details,
                           logo_file=logo_file,
                           data=model.station_data,
                           affected=affected,
                           color=color)


def get_random_logo():
    files = list(filter(lambda x: x.endswith('png'),
                        os.listdir(f'{app.static_folder}/images')))
    return random.choice(files)


def condense_affected_data():
    details = []
    for station in model.affected_station_data:
        # station contains two dataframes, one for before and after shock
        unit = station.name
        unit_details = model.details[model.details.unit == unit]
        name = unit_details['station'].iloc[0]
        line = unit_details['line'].iloc[0]
        color = unit_details['color'].iloc[0]
        details.append((name, line, color, station))
    return details
