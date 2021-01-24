import os
import sqlite3

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

# 'incomplete', 'complete', 'archived' (soft delete),
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

def get_todo_count():
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM items')

    return cursor.fetchone()[0]


def add_item(item_description):
    conn = get_connection()
    
    sql = f'''
    INSERT INTO items (
        description
    )
    VALUES (
        '{item_description}'
    )

    '''

    conn.cursor().execute(sql)
    conn.commit()

# TODO change status instead of hard deleting
def delete_item_by_row_number(item_row_num):
    # We cannot use PK for row number so we get the offset
    # and trust it's consistent since we are only reading/writing
    # from one local instance.
    # row number requires version 3. something and we only have 2.6.0
    # we can do this without row number simply by using offset
    offset = int(item_row_num) - 1
    # TODO: parametrize
    sql = f'''
    DELETE FROM items
    WHERE id IN
    (
    SELECT id FROM items LIMIT 1 OFFSET {offset}
    )
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    if cursor.rowcount == 1:
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def delete_item_by_description(item_description):
    # TODO: tokenize to get better matches?
    sql = f'''
    DELETE FROM items
    WHERE description LIKE '%{item_description}%'
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
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
        description, status
    FROM items
   
    '''

    cursor = get_connection().cursor()
    cursor.execute(sql)
    return cursor.fetchall()
