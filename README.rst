Insight Project
===============

Work for my Insight project on the effect of openings and closures on the
MTA subway in part and in whole, as part of my time during the summer 2017
session in NYC. The work can also be explored graphically at
`switchyard.site <https://switchyard.site>`_
(`GitHub repo <https://github.com/mmoran0032/switchyard.site>`_).


Pipeline
--------

Running the entire pipeline and analysis from a clean directory is
accomplished by the following:

#.  Create the directories ``raw_data``, ``processed_data`` within the project
    root directory. These directories are where the files pulled from the MTA
    and the files separated out by station will be kept.

#.  Run ``pull_turnstile_data.py``, which will grab all of the full-week
    turnstile data files from the MTA and save them in a directory called
    ``raw_data``. The files generated before 2014-10-18 have a slightly
    different format than the current format, requiring a different parsing
    routine to be used.

#.  Run ``combine_data.py`` loads the raw data into a PostgreSQL database
    called ``raw_stations`` in a table called ``raw``. This defaults to only
    looking at those files generated since 2014-10-18 (which use the current
    format). To include all data, pass in the flag ``--all`` when running.

    *Note that this does take a long time to finish, especially when loading*
    *in all of the data! Rough times per file are ~1 minute, so total time*
    *to load everything into PostgreSQL is ~6 hours (on my machine).*

    The data loaded into this frame is temporary, since we haven't handled
    finding actual ridership through the individual stations yet, and this
    database may be removed following the next step.

#.  Create the ridership tables for each station by running the
    ``data_reduction.ipynb`` notebook, since the process is not currently in
    a script. This file creates a new database called ``fullstations`` that
    contains a separate table for each unit and a table called ``details`` that
    contains the unit number, station name, lines serviced, and the line color.

    For most stations, the entrance/exit information is processed by a single
    unit. Larger stations (e.g. Grand Central, Penn Station, etc.) are serviced
    by multiple units. Those disparate units could be combined into a single
    super-unit table if desired, but that was not done for this work.

#.  The station relationships can be built by running ``run_single.py``.
    Currently, the values required to run the script (including the database
    and usernames) are hard-coded into the file. Command line arguments will be
    added in at a future date.

    This script creates a file ``name_of_event.csv`` (where ``name_of_event``
    is provided by the user) containing the "important" relations between the
    station closure/opening and the others on the system. In cases where
    multiple stations open or close at the same time, the relation is taken to
    be the same for all stations based on the total change at the stations.


Repository Structure
--------------------

-   The root directory contains the main processing scripts for the full
    pipeline, this README, and any additional information required.

-   ``exploratory_data_cleaning`` contains the notebooks that were used during
    the initial stages of the work. They are currently unfiltered and unordered
    and are taken as the "logbook" of my time at Insight working the problem.

-   ``raw_data`` contains the pulled turnstile data plus the field descriptions
    for the two types of files used by the MTA (pre-October 2014 and modern).
    This directory is not checked in and should be created by the user to hold
    the required data.

-   ``processed_data`` contains the CSV files containing the relationship
    between the station closure and openings to the other stations. These files
    should be intelligently combined before use.


Data Source
-----------

MTA turnstiles: `http://web.mta.info/developers/turnstile.html
<http://web.mta.info/developers/turnstile.html>`_
