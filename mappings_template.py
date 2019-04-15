import pandas as pd
from datetime import date
from tags_template import *

def get_mapping(df):
    # Each element in this list be a tuple containing two elements: a python predicate (which can be a combination by
    # using the '&' or '|') and a list of tags, imported from the tags.py file
    return [
        # Example:
        ((df['date'] == pd.Timestamp(date(2016, 6, 27))) & (df['other_account'] == 'some_account'), [GROCERIES]),
    ]