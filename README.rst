Insight Project
===============

Work for my Insight project on the effect of openings and closures on the
MTA subway in part and in whole, as part of my time during the summer 2017
session in NYC.

Running the entire pipeline and analysis from a clean directory is
accomplished by the following:

1.  Create the directories ``raw_data``, ``processed_data`` within the project
    root directory. These directories are where the files pulled from the MTA
    and the files separated out by station will be kept.

1.  Run ``pull_turnstile_data.py``, which will grab all of the full-week
    turnstile data files from the MTA and save them in a directory called
    ``raw_data``. The files generated before 2014-10-18 have a slightly
    different format than the current format, requiring a different parsing
    routine to be used.

1.  Run ``combine_data.py`` loads the raw data into a PostgreSQL database
    called ``raw_stations`` in a table called ``raw``. This defaults to only
    looking at those files generated since 2014-10-18 (which use the current
    format). To include all data, pass in the flag ``--all`` when running.

    *Note that this does take a long time to finish, especially when loading*
    *in all of the data! Rough times per file are ~1 minute, so total time*
    *to load everything into PostgreSQL is ~6 hours (on my machine).*

    The data loaded into this frame is temporary, since we haven't handled
    finding actual ridership through the individual stations yet, and this
    database may be removed following the next step.

1.  Create the ridership tables for each station by running


Data Source
-----------

MTA turnstiles: `http://web.mta.info/developers/turnstile.html
<http://web.mta.info/developers/turnstile.html>`_
