#!/usr/bin/env python3


import numpy as np
import pandas as pd
import pymc3 as pm

import psycopg2


def main(date_start='2016-11-15', date_stop='2017-01-31'):
    conn = create_connection()
    units = get_unit_list(conn)
    query = build_large_query(units, date_start, date_stop)
    data = pull_data(query, conn)
    print(data.index[:5])


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
    return df.unit.unique().tolist()


def build_large_query(units, start, stop):
    select = '{}.enter {}_enter, {}.exit {}_exit'
    join = 'full outer join {} on r001.date_time = {}.date_time'
    select_parts = ',\n'.join(select.format(u, u, u, u) for u in units)
    start_station = units.pop(0)
    join_parts = '\n'.join(join.format(u, u) for u in units)
    query = f'''
        select {start_station}.date_time, {select_parts}
        from {start_station} {join_parts}
        where {start_station}.date_time between '{start}' and '{stop}'
        order by date_time asc;
    '''
    return query


def pull_data(query, conn):
    df = pd.read_sql(query, conn).set_index('date_time')
    df.index = df.index.tz_convert('EST')
    # return df.groupby('date')[['enter', 'exit']].sum().reset_index()
    return df


def get_model_results(data, sample=1000, tune=500):
    with pm.Model() as model:
        mu = data.mean()
        lambda_1 = pm.Poisson('lambda_1', mu)
        lambda_2 = pm.Poisson('lambda_2', mu)
        tau = pm.DiscreteUniform('tau', lower=0, upper=data.shape[0])
        idx = np.arange(data.shape[0])  # Index
        lambda_ = pm.math.switch(tau >= idx, lambda_1, lambda_2)
        observation = pm.Poisson('obs', lambda_, observed=data.values)
        step = pm.Metropolis()
        trace = pm.sample(sample, tune=tune, step=step)
    return trace


def find_relation(trace_1, trace_2):
    t1l1 = trace_1['lambda_1'][5000:].mean()
    t1l2 = trace_1['lambda_2'][5000:].mean()
    t2l1 = trace_1['lambda_1'][5000:].mean()
    t2l2 = trace_1['lambda_2'][5000:].mean()
    delta_1 = t1l2 - t1l1
    delta_2 = t2l2 - t2l1
    return delta_1 / delta_2


if __name__ == '__main__':
    main()
