============
fileorganize
============

Utility functions for corpus and experiment file management in Python.

============
Installation
============

.. code-block:: Python
		
  pip install fileorganize

=============
Documentation
=============

========
Examples
========

.. code-block:: Python

  from fileorganize import dir_to_df

  # Get all files in `mypath` as a dataframe
  df = dir_to_df(mypath)

  # Get all `.wav` files in `mypath` as a dataframe
  df = dir_to_df(mypath, fnpat=r'\.wav$')

  # Get all `.wav` files in `mypath` and extract named captures as
  # categorical `subj` and `token` columns
  df = dir_to_df(
      mypath,
      fnpat=r'(?P<subj>[A-Z]+\d+)-(?P<token>\d+)\.wav$'
  )

.. code-block:: Python

  from fileorganize import today_YYYYMMDD, timestamp_now

  # Get today's date in YYYYMMDD format
  todaystr = today_YYYYMMDD()

  # Get timestamp as YYYY-MM-DDTHHMMSS string and UTC offset for current
  # the current datetime
  tstamp, utcoffset = timestamp_now()

.. code-block:: Python

  from fileorganize import cp_backup

  # Copy a file to a backup directory with a version number
  copyname = cp_backup(origfile, backupdir)
