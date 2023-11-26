import sqlite3
import pandas as pd

#load the data from csv file 
df = pd.read_csv('data.csv', low_memory=False)

#connect to the database
conn = sqlite3.connect('db.sqlite3')

#insert the data into the database
df.to_sql('data', conn, if_exists='append', index=False)

# close the connection
conn.close()