import os
import re
import pickle
import pandas as pd
import numpy as np

import ascii_reader

# NOTES
# vars from 1984 data
# didn't include because not included in all years
# ACC HD WORK HOURS(10038),
# AGE OLDEST KID (10974)

# QUESTIONS
# use combined or head income?

# Covariates used in the model
# DO NOT EDIT THIS
COVS = {
    # covs of current year
    # 17-97, 98, 99: NA
    'age of head': [10419],
    # 1~5, 8:DK, 9: NA
    'health of head': [10877, 11991, 13417, 23180],
    # 0, 1-51, 99: NA
    'current state': [10003],
    # 1-8
    'employment status': [10453, 11637],
    # 1-8, 9: NA/DK
    # map: 9:NAN
    'employment status2': [22448],
    # values: 0-8
    'number of children': [10422, 22409],

    # covs of previous year
    # 0, 1-99998, 999999
    'income of head': [11023],
    # 0, 1-999998, 9999999
    # map: simply combine two columns
    'income of head2': [23323],
    # 0, 1-5840
    'work hours': [10037, 11146, 21632],
    # income / wrk hrs
    'hourly earning of head': [11026],
    # .01`997.99, .00, 998, 999
    # map: recalculate this using income/wrk hrs
    'hourly earning of head2': [22470],

    # constant covs
    # 1-8, 9:NA/DK
    # combine 4,5;
    # 0 is read/write but taken out since '85
    'education': [12400],
    # 0(no grades), 1-16 (actual grade), 17 (postgrad), 99 (NA/DK)
    # map: 0-5: 1, 6-8:2, 9-11:3, 12:4, 13-15:6, 16:7, 17:8, 99:9
    'education2': [21504]
}

YEARS = range(1984, 1994)
FILE_PATH = 'data/fam'
FILE_KEY = 'fam'
NAME_KEY = FILE_KEY.upper()
VAR_KEY = 'V'
IS_FAM = True


def get_dir_path(year):
    return os.path.join(FILE_PATH, FILE_KEY + str(year))


def get_export_path():
    return os.path.join(FILE_PATH, FILE_KEY + '_clean.csv')


def get_pickle_path(year):
    return os.path.join(get_dir_path(year), NAME_KEY + str(year) + '.pickle')


def get_csv_path(year):
    return os.path.join(get_dir_path(year), NAME_KEY + str(year) + '.csv')


def get_pickle(year):
    with open(get_pickle_path(year), 'rb') as f:
        return pickle.load(f)


def parse_name(s):
    """Parses name of variable to find common variable across years"""
    # remove question number (ex. B2-1 EMPLOYMENT...)
    s = re.sub('^[A-Z][0-9]+(-[0-9]+)? ', '', s)
    # remove all characters except capital alphabet (including space)
    return re.sub('[^A-Z]', '', s)


def validate_covs(years):
    """Checks that the variables in COVS are present in all years.
    Prints the number of each COV. This number should match number of years.
    """
    all_lab2name = {}
    for y in years:
        lab2name, _ = get_pickle(y)
        # python 3.5 syntax for merging dicts (overwrites keys of first dict)
        all_lab2name = {**all_lab2name, **lab2name}
    # cov2name is for printing
    cov2name = {}
    # name2cov is used to identify variables we need
    name2cov = {}
    for key in COVS.keys():
        cov2name[key] = []
        for lab in COVS[key]:
            parsed = parse_name(all_lab2name[VAR_KEY + str(lab)])
            cov2name[key].append(parsed)
            name2cov[parsed] = key

    # lab2cov is returned by function to be used to pick variables from dataframe
    lab2cov = {}
    # var_names is for printing
    var_names = []
    for lab, name in all_lab2name.items():
        parsed = parse_name(name)
        if parsed in name2cov:
            var_names.append(name2cov[parsed])
            lab2cov[lab] = name2cov[parsed]

    v = pd.Series(var_names).value_counts().sort_values()
    print(cov2name)
    i = v.index.sort_values()
    print(v[i])
    return lab2cov


def main():
    # parse data from raw ascii file
    # only run this if file not already in csv format
    for y in YEARS:
        print('\n')
        print('Processing year {0}'.format(y))
        r = ascii_reader.ascii_(get_dir_path(y), NAME_KEY + str(y), IS_FAM)
        inds, headers, lab2format, _, _ = r.read_index_file()
        data_path = r.read_data_file(inds, headers, lab2format)

    lab2cov = validate_covs(YEARS)

    # combine covariates
    dfs = []
    for y in YEARS:
        temp_df = pd.DataFrame()
        # read in raw data
        raw_df = pd.read_csv(get_csv_path(y))
        variables = [c for c in raw_df.columns if c in lab2cov]
        for v in variables:
            temp_df[lab2cov[v]] = raw_df[v]
        temp_df['year'] = y
        dfs.append(temp_df)
    df = pd.concat(dfs, axis=0, join='outer')

    # merging columns and re-evaluating variables
    df['employment status'] = df['employment status'].fillna(
        df['employment status2'])
    del df['employment status2']
    df['income of head'] = df['income of head'].fillna(df['income of head2'])
    del df['income of head2']
    df['hourly earning of head'] = df['hourly earning of head'].fillna(
        df['hourly earning of head2'])
    del df['hourly earning of head2']
    ed = df['education2']
    df.loc[(ed >= 0) & (ed <= 5), 'education'] = 1
    df.loc[(ed >= 6) & (ed <= 8), 'education'] = 2
    df.loc[(ed >= 9) & (ed <= 11), 'education'] = 3
    df.loc[ed == 12, 'education'] = 4
    df.loc[(ed >= 13) & (ed <= 15), 'education'] = 6
    df.loc[ed == 16, 'education'] = 7
    df.loc[ed == 17, 'education'] = 8
    df.loc[ed == 99, 'education'] = 9
    del df['education2']

    df.shape
    df.head()
    df.describe()

    df.loc[df['age of head'] == 99, 'age of head'] = np.NaN
    df.loc[df['education'] == 9, 'education'] = np.NaN
    df.loc[(df['health of head'] == 8)
           | (df['health of head'] == 9), 'health of head'] = np.NaN
    df.loc[df['current state'] == 99, 'current state'] = np.NaN
    df.loc[df['employment status'] == 9, 'employment status'] = np.NaN

    df['hourly earning of head'] = df['income of head'] / df['work hours']
    no_work = df['work hours'] == 0
    df.loc[no_work, 'hourly earning of head'] = 0

    df.to_csv(get_export_path())


if __name__ == "__main__":
    # execute only if run as a script
    main()
