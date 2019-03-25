import os


def get_account_nr(filename):
    basename = os.path.splitext(os.path.basename(filename))[0]
    return basename.split('(')[0]

def remove_intra_transactions(df, accounts_list):
    """Remove transactions that are going from one of my accounts to another one"""
    return df[~df['other_account'].str.replace(' ', '').isin(list(df['account'].unique()) + accounts_list)]