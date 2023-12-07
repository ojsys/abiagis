import sqlite3
import pandas as pd

#load the data from csv file 
df = pd.read_csv('percel_data.csv', low_memory=False)
#df = pd.read_csv('lines.csv', low_memory=False)
#connect to the database
conn = sqlite3.connect('db.sqlite3')

#insert the data into the database
df.to_sql('coapp_parcel', conn, if_exists='replace', index=False)
#df.to_sql('coapp_lines', conn, if_exists='replace', index=False)

# close the connection
conn.close()