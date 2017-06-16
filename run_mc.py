#!/usr/bin/env python3


# import pymc3 as pm

# import numpy as np
import pandas as pd

from sqlalchemy import create_engine
import psycopg2


tables = ['second72', 'second86', 'second96',
          'g68', 'g77', 'g86', 'g96',
          'g103', 'g110', 'g116', 'g125']
renames = ['s72', 's86', 's96',
           'g68', 'g77', 'g86', 'g96',
           'g103', 'g110', 'g116', 'g125']

# select = '{}.d_entries {}_in, {}.d_exits {}_out'
select = '{}.d_entries {}_in'
joins = 'left join {} {} on l.date = {}.date'

# select_parts = ['select l.date, l.d_entries l_in, l.d_exits l_out']
select_parts = ['select l.date, l.d_entries l_in']
join_parts = ['from lexington l']
for old, new in zip(tables, renames):
    new_select = select.format(new, new, new, new)
    select_parts.append(new_select)
    new_join = joins.format(old, new, new)
    join_parts.append(new_join)
select_str = ',\n'.join(select_parts)
query = '\n'.join([select_str, *join_parts, ';'])

user = 'mikemoran'
host = 'localhost'
dbname = 'stations'

engine = create_engine(f'postgres://{user}@{host}/{dbname}')
conn = None
conn = psycopg2.connect(database=dbname, user=user)

df = (pd.read_sql_query(query, conn, parse_dates=['date'])
        .set_index('date', drop=True)
        .sort_index())
