import sqlite3
# Create a database
conn = sqlite3.connect('example.db')

#sqlite3 is a module



conn.row_factory = sqlite3.Row  #to access columns,This means that the database 
#connection will return rows that behave like regular Python dictionaries.

# Make a convenience function for running SQL queries
def sql_query(query):
    conn = sqlite3.connect('example.db')#otherwise error SQLite objects created in a thread can only be used in that same thread
    conn.row_factory = sqlite3.Row#will not get displayed 
    cur = conn.cursor() #allows you to process rows in a database
    cur.execute(query)
    rows = cur.fetchall()
    return rows 

def sql_edit_insert(query,var):
    conn = sqlite3.connect('example.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query,var)
    conn.commit()  #for save
    return cur.rowcount
  

##def sql_delete(query,var):


def sql_query2(query,var):
    conn = sqlite3.connect('example.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query,var)
    rows = cur.fetchall()
    return rows

