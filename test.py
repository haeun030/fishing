import pandas as pd
import sqlite3

con = sqlite3.connect('./users.db')

df = pd.read_sql('SELECT * FROM users',con)

df = pd.read_sql('users', con)