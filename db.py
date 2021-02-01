import os
import sqlite3
from datetime import datetime


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


# 'incomplete', 'complete', 'archived' (soft delete),
create_sql = '''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'incomplete',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
)
'''


def get_connection(db_path=DEFAULT_PATH):
    return sqlite3.connect(db_path)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(create_sql)
    cursor.close()

    return conn


def add_item(item_description):
    sql = f'''
    INSERT INTO items (
        description
    )
    VALUES (
        ?
    )
    '''
    conn = get_connection()
    conn.cursor().execute(sql, (item_description,))
    conn.commit()


def fetch_item_by_row_number(row_number):
    offset = int(row_number) - 1

    sql = '''
    SELECT 
        id, 
        description
    FROM items
    WHERE status = 'incomplete'
    LIMIT 1
    OFFSET ?
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (offset,))
    return cursor.fetchone()


def fetch_item_by_description(description):
    '''
    Looks for an exact on the provided item description.
    If nothing is found, tokenizes the description
    and looks for an unambiguous partial match.
    '''

    full_match_sql = '''
    SELECT 
        id, 
        description
    FROM items
    WHERE 
        status = 'incomplete'
        AND description LIKE ?
    '''
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(full_match_sql, (description,))
    full_match = cursor.fetchone()
    if full_match is not None:
        return full_match

    tokens = [
        f'%{t}%' for t in description.split(' ')
    ]
    like_query = ' OR '.join(
        ['description LIKE ?' for t in tokens]
    )
    partial_match_sql = f'''
    SELECT 
        id, 
        description
    FROM items
    WHERE 
        status = 'incomplete'
        AND (
            {like_query}
        )
    '''
    cursor.execute(partial_match_sql, tuple(tokens))
    # We're doing a pretty generous match, so only
    # return a result if it's unambiguous
    results = cursor.fetchall()
    if len(results) == 1:
        return results[0]
    return None


def close_item(item_id, close_status):
    sql = '''
    UPDATE items
    SET 
        status = ?,
        closed_at = CURRENT_TIMESTAMP
    WHERE id = ?
    LIMIT 1
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (close_status, int(item_id),))
    if cursor.rowcount == 1:
        conn.commit()
        return True
    return False


def get_active_items():
    conn = get_connection()

    sql = '''
    SELECT
        description
    FROM items
    WHERE
        status = 'incomplete'
    '''

    cursor = get_connection().cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def get_random_active_item():
    sql = '''
    SELECT
        description
    FROM items
    WHERE
        status = 'incomplete'
    ORDER BY RANDOM()
    LIMIT 1
    '''
    
    cursor = get_connection().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0] if result else None


def get_num_completed_items():
    sql = '''
    SELECT COUNT(1)
    FROM items
    WHERE
        status = 'complete'
    '''
    
    cursor = get_connection().cursor()
    cursor.execute(sql)
    return cursor.fetchone()[0]


def get_earliest_created_time():
    sql = '''
    SELECT created_at
    FROM items
    ORDER BY created_at
    LIMIT 1
    '''
    cursor = get_connection().cursor()
    cursor.execute(sql)
    res = cursor.fetchone()
    if res is None:
        return None
    return datetime.strptime(res[0], '%Y-%m-%d %H:%M:%S')


def get_latest_completed_time():
    sql = '''
    SELECT closed_at
    FROM items
    WHERE status = 'complete'
    ORDER BY closed_at DESC
    LIMIT 1
    '''
    cursor = get_connection().cursor()
    cursor.execute(sql)
    res = cursor.fetchone()
    if res is None:
        return None
    return datetime.strptime(res[0], '%Y-%m-%d %H:%M:%S')


def get_average_days_to_completion():
    sql = '''
    SELECT 
        AVG( julianday(closed_at) - julianday(created_at) )
    FROM items
    WHERE status = 'complete'
    '''
    cursor = get_connection().cursor()
    cursor.execute(sql)
    res = cursor.fetchone()
    if res is None:
        return None
        
    return round(res[0])
