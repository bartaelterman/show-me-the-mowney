import click
import data_parsers
import numpy as np
import pandas as pd
import utils
import yaml

from mappings import get_mapping


def load_all_data():
    """Read data from argenta old, argenta new and ING and concatenate all payments"""
    settings = yaml.load(open('config.yaml'))
    dfs = []
    for data in settings['data']:
        parser = getattr(data_parsers, data['parser'])
        account = data['account'] if 'account' in data.keys() else None
        df = parser(path=data['path'], account=account)
        dfs.append(df)
    df = pd.concat(dfs, sort=False)
    df['announcement2'].fillna('', inplace=True)
    df.drop('date2', axis=1, inplace=True)
    df = df.drop_duplicates()
    cleanup_accounts(df)
    df = utils.remove_intra_transactions(df, settings['accounts'])
    df.index = pd.Index(range(len(df)))
    df['pmt_year'] = df['payment_date'].dt.year
    df['pmt_month'] = df['payment_date'].dt.month
    df['pmt_id'] = df.index
    df['other_name'] = df['other_name'].astype(str)
    df['description'] = df['description'].astype(str)
    return df


def get_main_payers(df, top=10):
    incomes = df[df['amount'] > 0]
    g = incomes[['amount', 'other_name', 'other_account']].groupby(['other_name', 'other_account']).sum()
    return g['amount'].sort_values(ascending=False)[:top]


def get_main_expenses(df, top=10):
    expenses = df[df['amount'] < 0]
    g = expenses[['amount', 'other_name', 'other_account']].groupby(['other_name', 'other_account']).sum()
    return g['amount'].sort_values()[:top]


def cleanup_accounts(df):
    df['other_account'] = df['other_account'].str.replace('-', '')
    df['other_account'] = df['other_account'].str.replace(' ', '')
    df['account'] = df['account'].str.replace('-', '')
    df['account'] = df['account'].str.replace(' ', '')


def tag_payments(df):
    df['tag_1'] = np.nan
    df['tag_2'] = np.nan
    df['tag_3'] = np.nan
    # embed()
    for mapping in get_mapping(df):
        predicate, tags = mapping
        for i, tag in enumerate(tags):
            if type(tag) == dict:
                tag_ = tag['label']
            else:
                tag_ = tag
            df.loc[(predicate & df['tag_1'].isnull()), 'tag_' + str(i+1)] = tag_


def tagging_report(df,):
    """Give some insights into which payments are tagged and which are not"""
    df['tagged'] = ~df['tag_1'].isnull()
    m = df.loc[:, ['amount', 'pmt_year', 'tagged']].drop_duplicates()
    print('\nSum of tagged and untagged payments per year:\n=========\n')
    print(m.groupby(['tagged', 'pmt_year']).sum())


def cluster_payments(df):
    """
    Create clusters of similar payments based on account number and other_name.
    Next we could sum by cluster to find expensive recurring payments.
    We could even check whether it is really a recurring payment by checking the variability between payments within a
    cluster.
    """
    pass


def monthly_report(df, tag):
    report_per_year = df.loc[df['tag_1'] == tag, ['amount', 'other_name', 'pmt_year']].groupby(['pmt_year', 'other_name']).sum()
    print(f'Expenses on {tag}:')
    print(report_per_year.sort_values(['pmt_year', 'amount']))


@click.group()
def cli():
    pass

@cli.command()
def tag_report():
    df = load_all_data()
    tag_payments(df)
    tagging_report(df)

@cli.command()
def main_payers():
    """Show the main sources of income"""
    df = load_all_data()
    print('main payers:')
    print(get_main_payers(df))
    print('')

@cli.command()
def main_expenses():
    """Get the overall main expenses"""
    df = load_all_data()
    print('main expenses:')
    print(get_main_expenses(df))
    print('')

@cli.command()
def expenses_by_tag():
    """Show the main expenses for a selection of tags"""
    df = load_all_data()
    tag_payments(df)
    monthly_report(df, 'car')
    print('\n-----------------\n')
    monthly_report(df, 'house')
    print('\n-----------------\n')
    monthly_report(df, 'groceries')
    print('\n-----------------\n')
    monthly_report(df, 'kids')


@cli.command()
def budget_overview():
    """print the estimated budgets"""
    pass


@cli.command()
def budget_per_year():
    """print the expenses per tag per year"""
    df = load_all_data()
    tag_payments(df)
    year_groups = df[['amount', 'pmt_year', 'tag_1']].groupby('pmt_year')
    out = pd.DataFrame()
    year_balances = {}
    for name, group in year_groups:
        summed_amount = group[['amount', 'tag_1']].groupby('tag_1').sum()['amount']
        out[name] = summed_amount
        year_balances[name] = summed_amount.sum()

    print(out)
    print(year_balances)

if __name__ == '__main__':
    cli()