import os
import sqlite3

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

# 'incomplete', 'complete', 'archived' (soft delete),
# TODO define constants
create_sql = '''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'incomplete',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
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
    conn = get_connection()
    
    sql = f'''
    INSERT INTO items (
        description
    )
    VALUES (
        ?
    )

    '''

    conn.cursor().execute(sql, (item_description,))
    conn.commit()

def fetch_item(log, row_number):
    log.info(row_number)
    offset = int(row_number) - 1

    sql = '''
    SELECT id, description
    FROM items
    WHERE status = 'incomplete'
    LIMIT 1
    OFFSET ?
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (offset,))
    return cursor.fetchone()
    #return result[0] if result else None


def close_item(log, item_id, close_status):
    log.info(f'item id: {item_id}, close status: {close_status}')
    sql = '''
    UPDATE items
    SET 
        status = ?
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

def close_item_by_row_number(item_row_num, close_status):
    # We cannot use PK for row number so we get the offset
    # and trust it's consistent since we are only reading/writing
    # from one local instance.
    # row number requires version 3. something and we only have 2.6.0
    # we can do this without row number simply by using offset
    # TEST: duplicate descriptions where one is already closed
    offset = int(item_row_num) - 1
    sql = '''
    UPDATE items
    SET 
        status = ?
    WHERE status = 'incomplete'
    LIMIT 1
    OFFSET ?
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (close_status, offset,))
    if cursor.rowcount == 1:
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def close_item_by_description(item_description, close_status):
    # TODO: tokenize description and construct
    # ...OR LIKE... query to allow for partial matches
    description_param = f'%{item_description}%'
    sql = '''
    UPDATE items
    SET
        status = ?
    WHERE 
        status = 'incomplete'
        AND description LIKE ?
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (close_status, description_param,))
    if cursor.rowcount == 1:
        conn.commit()
        conn.close()
        return True
    conn.close()

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
    return cursor.fetchone()


def get_average_completed_per_week():
    # a little tricky. need to know
    # # completed, timeframe (earliest started and now?),
    # and timeframe converted to # of weeks
    pass


def get_average_time_to_completion():
    '''

    '''