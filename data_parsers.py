import logging
import numpy as np
import os
import pandas as pd
import utils
from glob import glob


def load_data_ing(path, account):
    """Load all data files from ING and remove duplicate entries (in case data overlaps)"""
    files = glob(os.path.join(path, '*csv'))
    print(len(files))
    dfs_list = []

    for filename in files:
        df = pd.read_csv(
            filename,
            sep=';',
            decimal=',',
            header=1,
            names=['account', 'account_name', 'other_account', 'booking_nr', 'payment_date', 'date', 'amount', 'currency',
                   'description', 'detail', 'announcement'],
            skiprows=0,
            parse_dates=['date', 'payment_date'],
            date_parser=lambda x: pd.datetime.strptime(str(x), '%d/%m/%Y') if not pd.isnull(x) else np.nan,
            dtype={'amount': np.float64},
            encoding='latin-1'
        )
        df['account'] = account
        df['announcement'] = df['detail']
        dfs_list.append(df)
    full_df = pd.concat(dfs_list)
    full_df.fillna('', inplace=True)
    full_df.index = pd.Index(range(len(full_df)))
    logging.info(f'rows: {len(full_df)}')
    # In some cases, the "other_account" is empty. Often we can parse it from the description
    full_df.loc[(full_df['announcement'].isnull())
           & (full_df['other_account'] == '')
           & (full_df['description'].str.startswith('Aankoop')),
            'other_name'] = full_df.loc[(full_df['announcement'].isnull())
                                        & (full_df['other_account'].isnull())
                                        & (full_df['description'].str.startswith('Aankoop')),
                                        'description'].str.extract(' uur - (.*) -')[0]
    full_df.drop_duplicates()
    logging.info(f'rows after removing duplicates: {len(full_df)}')
    return full_df


def load_data_argenta_old(path, account=None):
    """Load all data files and remove duplicate entries (in case data overlaps)"""
    files = glob(os.path.join(path, '*csv'))
    print(len(files))
    dfs_list = []

    for filename in files:
        account_nr = utils.get_account_nr(filename)
        df = pd.read_csv(
            filename,
            sep=';',
            decimal=',',
            thousands='.',
            header=1,
            names=['date', 'reference', 'description', 'amount', 'currency', 'payment_date', 'other_account',
                   'other_name', 'announcement1', 'announcement2'],
            skiprows=0,
            parse_dates=['date', 'payment_date'],
            date_parser=lambda x: pd.datetime.strptime(x, '%d-%m-%Y'),
            dtype={'amount': np.float64},
            encoding='latin-1'
        )
        df['account'] = account_nr
        dfs_list.append(df)
    full_df = pd.concat(dfs_list)
    full_df.fillna('', inplace=True)
    full_df.index = pd.Index(range(len(full_df)))
    full_df['announcement2'] = full_df['announcement2'].str.strip()
    full_df['description'] = full_df['description'].str.replace('Overschrijving te uwen gunste',
                                                                'Inkomende overschrijving')
    logging.info(f'rows: {len(full_df)}')
    full_df.drop_duplicates()
    logging.info(f'rows after removing duplicates: {len(full_df)}')
    return full_df


def load_data_argenta(path, account=None):
    """Load all data files from the new argenta export format and remove duplicate entries"""
    files = glob(os.path.join(path, '*xlsx'))
    print(len(files))
    dfs_list = []

    for filename in files:
        df = pd.read_excel(
            filename,
            decimal=',',
            thousands='.',
            names=['account', 'date', 'date2', 'reference', 'description', 'amount', 'currency',
                        'payment_date', 'other_account', 'other_name', 'announcement1'],
            date_parser=lambda x: pd.datetime.strptime(x, '%d-%m-%Y'),
            dtype={'amount': np.float64},
            encoding='latin-1'
        )
        df['date'] = pd.to_datetime(df['date'])
        df['date2'] = pd.to_datetime(df['date2'])
        df['payment_date'] = pd.to_datetime(df['payment_date'])
        dfs_list.append(df)
    full_df = pd.concat(dfs_list)
    full_df.index = pd.Index(range(len(full_df)))
    full_df.fillna('', inplace=True)
    logging.info(f'rows: {len(full_df)}')
    full_df.drop_duplicates()
    logging.info(f'rows after removing duplicates: {len(full_df)}')
    return full_df
