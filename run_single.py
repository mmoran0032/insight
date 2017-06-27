#!/usr/bin/env python3


import numpy as np
import pandas as pd
import pymc3 as pm

import psycopg2


# mix of large stations and PATH data
exclude = ['R010', 'R011', 'R012', 'R020', 'R021', 'R022', 'R031', 'R032',
           'R033', 'R045', 'R046', 'R047', 'R048', 'R072', 'R195', 'R293',
           'R328', 'R469', 'R535', 'R536', 'R541', 'R545', 'R547', 'R548',
           'R549', 'R550', 'R552']


def main(date_start='2016-11-15', date_stop='2017-02-15', shock='2017-01-01',
         name_of_event='second_avenue_opens',
         units_changed=['R570', 'R571', 'R572']):
    conn = create_connection()
    units = get_unit_list(conn)
    query = build_large_query(units, date_start, date_stop)
    data = resample(pull_data(query, conn))
    saved_traces = prediction(data)
    filtered = filter_traces(units, saved_traces, data.index.get_loc(shock))
    create_and_save_dataframe(filtered, units_changed, name_of_event)


def create_connection():
    user = 'mikemoran'
    dbname = 'fullstations'
    return psycopg2.connect(database=dbname, user=user)


def get_unit_list(conn):
    query = '''
        select distinct unit from details
            order by unit asc;
    '''
    df = pd.read_sql(query, conn)
    units = df.unit.unique().tolist()
    return [u for u in units if u not in exclude]  # removes major stations


def build_large_query(units, start, stop, include_exit=True):
    ''' build out a large SQL query that pulls all units (stations)
        entrance and potentially exit data
    '''
    select = '{}.enter {}_enter, {}.exit {}_exit'
    if not include_exit:
        select = '{}.enter {}'
    join = 'full outer join {} on r001.date_time = {}.date_time'
    select_parts = ',\n'.join(select.format(u, u, u, u) for u in units)
    start_station = units[0]
    join_parts = '\n'.join(join.format(u, u) for u in units[1:])
    query = f'''select {start_station}.date_time, {select_parts}
        from {start_station} {join_parts}
        where {start_station}.date_time between '{start}' and '{stop}'
        order by date_time asc;
    '''
    return query


def pull_data(query, conn):
    df = (pd.read_sql(query, conn, parse_dates=['date_time'])
            .set_index('date_time'))
    try:
        df.index = df.index.tz_convert('EST')
    except TypeError:
        df.index = df.index.tz_localize('EST')
    df.index = pd.DatetimeIndex(df.index)
    df.columns = df.columns.str.upper()
    return df


def resample(dataframe):
    df = dataframe.resample('1D', closed='right').sum()
    df['date'] = df.index.date
    df.set_index('date', inplace=True)
    df.index = pd.DatetimeIndex(df.index)
    return df.iloc[1:]  # to remove the partial starting day


def prediction(data):
    saved_traces = {}
    for station in data.columns:
        df = data[station].fillna(0)
        trace = get_model_results(df, sample=10000, tune=5000)
        saved_traces[station] = trace[5000:]
    return saved_traces


def get_model_results(data, sample=8000, tune=4000):
    with pm.Model() as model:
        mu = data.mean()
        lambda_1 = pm.Poisson('riders_before', mu)
        lambda_2 = pm.Poisson('riders_after', mu)
        tau = pm.DiscreteUniform('day_of_shock', lower=0, upper=data.shape[0])
        idx = np.arange(data.shape[0])  # Index
        lambda_ = pm.math.switch(tau >= idx, lambda_1, lambda_2)
        observation = pm.Poisson('observed', lambda_, observed=data.values)
        step = pm.Metropolis()
        trace = pm.sample(sample, tune=tune, step=step)
    return trace


def filter_traces(traces, shock):
    filtered = {}
    for unit, trace in traces.items():
        before = trace.get_values('riders_before').mean()
        after = trace.get_values('riders_after').mean()
        date = trace.get_values('day_of_shock').mean()
        if ((shock - 3 < date < shock + 3) and  # day needs to be near actual
                (np.abs(after - before) > 1000)):  # larger changes only
            filtered[unit] = after - before
    return filtered


def create_and_save_dataframe(data, changed, name):
    df = pd.DataFrame(data, index=changed).transpose()
    # handle "forward" change
    changed_riders = df.loc[changed].iloc[:, 0].sum()
    df = df / changed_riders
    for unit in df.index:
        if unit not in df.columns:
            df[unit] = np.NaN
    df = df[sorted(df.columns)]
    df.loc[changed] = (1 - df[changed].transpose()) / len(changed)
    df.loc[changed, changed] = 0
    df.to_csv(f'{name}.csv')


if __name__ == '__main__':
    main()
