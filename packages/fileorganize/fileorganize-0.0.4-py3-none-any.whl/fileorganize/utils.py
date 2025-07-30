# Utility functions.
__all__=['today_YYYYMMDD', 'timestamp_now', 'cp_backup', 'dir_to_df']

import os
import pandas as pd
import numpy as np
import re
import fnmatch
import shutil
from datetime import datetime
import dateutil

def dir_to_df(dirname, fnpat=None, dirpat=None, addcols=[], sentinel='',
to_datetime=True, dotfiles=False, dotdirs=False, sort_by=['relpath', 'fname'], **kwargs):
    '''`dir_to_df`: Recursively generate the filenames in a directory tree
using `os.walk` and store as rows of a DataFrame.

'Hidden' files and directories (those with names that start with '.') are
ignored by default. `dir_to_df` will also not descend into a directory tree that
contains a sentinel file.

Additional parameters can be used to filter which filepaths to include in the
output, and also to add additional file metadata.

Parameters
----------

dirname : str
    Top-level directory name for filename search.


Optional parameters
-------------------

fnpat : str, re
    Regular expression pattern that defines the filenames to return.
    The only filenames in the result set will be those that return a match
    for `re.search(fnpat, filename)`.

    If you use named captures in `fnpat`, new columns corresponding to the
    capture groups will be added to the output dataframe as dtype 'Categorical'.

    If you need to use a flag with your pattern, you can use a precompiled
    regex for the value of `fnpat`. For example, you can do
    case-insensitive matching with `re.compile(pattern, re.IGNORECASE)`.

dirpat : str, re
    Same as `fnpat`, only applied against the relative path in dirname.
    Relative paths that do not match `dirpat` will be skipped.

addcols = str, list of str (default [])
    One or more additional columns to include in the output. Possible names
    and values provided are:
    'dirname': the user-provided top-level directory
    'barename': the filename without path or extension
    'ext': the filename extension
    'mtime': the last modification time of the file
    'bytes': the size of the file in bytes

    The 'mtime' column is cast to Pandas Timestamps automatically unless
    `to_datetime` is False. Resolution of the time-based stats is dependent
    on your platform; see the `os.stat` documentation.

sentinel : str (default '')
    Name of the sentinel file, which marks a directory tree to be ignored. No
    filenames from the directory containing the sentinel file will be included
    in the output, nor will any filenames from any of its subdirectories.
    If the value of `sentinel` is '' or None, the sentinel file check will not
    be performed.

to_datetime : boolean (default True)
    If True, 'mtime' stats will be converted from Unix epoch to datetime.
    If False, the values will not be converted.

dotfiles : boolean (default False)
    If True, include filenames beginning with `.` in the output. Otherwise,
    omit these names.

dotdirs : boolean (default False)
    If True, descend into directories with names that begin with `.`. If
    False, do not descend into these directories.

sort_by : list of str (default ['relpath', 'fname']
    Sort output dataframe rows by the columns named in the list. Specify an empty
    list `[]` if no sorting is desired.

kwargs : various
    Remaining kwargs are passed to `os.walk`. If not used, then `os.walk` will
    be called with default kwargs. Note that using `os.walk(topdown=False)` is
    not compatible with `dotdirs=False`.


Returns
-------

fnamedf : DataFrame
    Dataframe of filename rows.

'''
    # Coerce addcols to list if passed as single string.
    try:
        assert isinstance(addcols, str)
        addcols = [addcols]
    except AssertionError:
        pass   # Should be a list already.

    if 'dirname' in addcols:
        firstcols = ['dirname', 'relpath', 'fname']
        addcols[:] = [c for c in addcols if c != 'dirname']
    else:
        firstcols = ['relpath', 'fname']
    mdcols = []  # Names of additional metadata columns from named captures.
    for pat in (dirpat, fnpat):
        if pat is None:
            continue
        pat = re.compile(pat)
        newmdcols = list(pat.groupindex.keys())
        for c in newmdcols:
            try:
                assert(c not in firstcols + addcols + mdcols)
            except AssertionError:
                msg = f'Named group {c} masks another output column.'
                raise RuntimeError(msg)
        mdcols += newmdcols

    stats = {'bytes': 'st_size'} if 'bytes' in addcols else {}
    if 'mtime' in addcols:
        stats['mtime'] = 'st_mtime'

    if dotdirs is False:
        try:
            assert(kwargs['topdown'] is True)
        except AssertionError:
            msg = '`topdown=False` not compatible with `dotdirs=False`'
            raise RuntimeError(msg)
        except KeyError:
            pass

    recs = []
    for root, dirs, files in os.walk(dirname, **kwargs):
        if sentinel in files:
            dirs[:] = []  # Do not descend into subdirectories.
            continue      # Do not include files in this directory.
        relpath = os.path.relpath(root, dirname)
        dircols = []
        if dirpat is not None:
            # TODO: don't call compile in this loop
            dirpat = re.compile(dirpat)
            dirm = dirpat.search(relpath)
            if dirm is None:
                continue # Do not include files in this directory.
            # Add named capture groups and replace unmatched optional
            # named captures with empty string.
            dircols = [
                '' if s is None else s for s in dirm.groupdict().values()
            ]
        for name in files:
            if (dotfiles is False) and (name[0] == '.'):
                continue
            fncols = []
            if fnpat is not None:
                # TODO: don't call compile in this loop
                fnpat = re.compile(fnpat)
                fnm = fnpat.search(name)
                if fnm is None:
                    continue # Do not include this file.
                # Add named capture groups and replace unmatched optional
                # named captures with empty string.
                fncols = [
                    '' if s is None else s for s in fnm.groupdict().values()
                ]
            reccols = []
            if stats != {}:
                st = os.stat(os.path.join(root, name))
            if ('barename' in addcols) or ('ext' in addcols):
                (barename, ext) = os.path.splitext(name)
            for col in firstcols + addcols:
                if col in ['bytes', 'mtime']:
                    reccols += [getattr(st, stats[col])]
                elif col == 'relpath':
                    reccols += [relpath]
                elif col == 'fname':
                    reccols += [name]
                elif col == 'dirname':
                    reccols += [dirname]
                elif col == 'barename':
                    reccols += [barename]
                elif col == 'ext':
                    reccols += [ext]
            recs.append(reccols + dircols + fncols)

        # Change dirs in-place to prevent os.walk() from descending into
        # '.' directories.
        if dotdirs is False:
            dirs[:] = [d for d in dirs if not d[0] == '.']

    df = pd.DataFrame(
        recs,
        columns=firstcols + addcols + mdcols
    )
    if sort_by != []:
        df = df.sort_values(
            by=sort_by, axis='rows'
        ).reset_index(drop=True)
    if len(df) > 0:
        # Cast named captured columns to Categorical.
        catcols = ['dirname', 'relpath', 'fname', 'barename', 'ext'] + mdcols
        df = df.astype({c: 'category' for c in df.columns if c in catcols})
        if to_datetime is True and 'mtime' in df.columns:
            df.loc[:, 'mtime'] = pd.to_datetime(df.loc[:, 'mtime'], unit='s')
    return df

def today_YYYYMMDD():
    """
    Return today's date in YYYYMMDD format.
    """
    return timestamp_now()[0].split('T')[0].replace('-', '')

def timestamp_now():
    """
    Create a timestamp for an acquisition, using current local time.

    Returns
    =======

    timestamp, utcoffset : tuple(str, str)
        A tuple of strings representing the datetime in YYYY-MM-DDTHHMMSS format and the timezone offset from UTC, e.g. '-0700'. 
    """

    # Regex that matches a timezone offset at the end of an acquisition
    # directory name.
    utcoffsetre = re.compile(
        r'(?P<offset>(?P<sign>[-+])(?P<hours>0\d|1[12])(?P<minutes>[012345]\d))'
    )
    timestamp = datetime.now(dateutil.tz.tzlocal()) \
             .replace(microsecond=0) \
             .isoformat() \
             .replace(":","")
    m = utcoffsetre.search(timestamp)
    utcoffset = m.group('offset')
    timestamp = utcoffsetre.sub('', timestamp)
    return (timestamp, utcoffset)

def cp_backup(fname, bkdir=None, hidden=True):
    """Make a backup copy of the file `fname` and return the name of the copied file. 

By default the copy will have the same name as `fname` with '.' prepended and a suffix of the form '.N', where N is an integer. Multiple calls to this function result in increasing values of N, starting with '1'.

Parameters
==========

fname : str
    The name of the file to be copied.

bkdir : str (default: None)
    By default, the backup file will be written in the same directory as the source file. If `bkdir` is provided, the backup file will be written to that path instead.  A `FileNotFoundError` will be thrown if the backup directory does not exist.

hidden : bool (default: True)
    If True, prepend '.' to the backup filename, resulting in a 'hidden' file. If not True, do not prepend anything.

Returns
=======

dst : str
    The name of the copied backup file.
    """
    
    if bkdir is None:
        bkdir = os.path.dirname(fname) if os.path.dirname(fname) != '' else '.'
    basename = os.path.basename(fname)
    cpname = '.' + basename if hidden is True else basename

    # Get extension integers from backups that already exist and find max N.
    rgx = re.compile(
        fnmatch.translate(cpname).replace('\\Z', '\\.[0-9]+\\Z')
    )
    Ns = np.array([
        int(os.path.splitext(f)[1].lstrip('.')) \
            for f in os.listdir(bkdir) if rgx.fullmatch(f)
    ], dtype=int)
    maxN = 0 if len(Ns) == 0 else Ns.max()

    cpname += '.{:d}'.format(maxN + 1)
    dst = os.path.join(bkdir, cpname)
    shutil.copyfile(fname, dst)
    return dst

