import os
import json
import hashlib
import pandas as pd

CACHE_DIR = "cache"

def ensure_cache_dir_exists():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_filename(query):
    '''
        Generate a consistent filename for a query.
    '''
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return os.path.join(CACHE_DIR, query_hash + ".json")

def store_in_cache(query, df, dividend_df=None):
    '''
        Store the data for a query in the cache.
    '''
    ensure_cache_dir_exists()
    cache_filename = get_cache_filename(query)
    
    data = {
        "Stock": df.to_json(date_format='iso', date_unit='ns'),
        "Dividend": None if dividend_df is None else dividend_df.to_json(date_format='iso', date_unit='ns')
    }

    with open(cache_filename, 'w') as f:
        json.dump(data, f)

def lookup_in_cache(query):
    '''
        Check if data for a query is in the cache. Return None if not found.
    '''
    cache_filename = get_cache_filename(query)
    
    if os.path.exists(cache_filename) and os.path.getsize(cache_filename) > 0:
        with open(cache_filename, 'r') as f:
            data = json.load(f)

        df = pd.read_json(data["Stock"], convert_dates=True)
        dividend_df = None if data["Dividend"] is None else pd.read_json(data["Dividend"], convert_dates=True)

        return df, dividend_df

    return None, None