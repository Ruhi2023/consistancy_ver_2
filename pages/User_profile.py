import streamlit as st 
import mysql.connector as conn
import pandas as pd 
import Consistancy_tables as su
my_host, my_user, my_passwd, dbname = su.getconnnames()

db = conn.connect(
    host = my_host,
    user = my_user,
    passwd = my_passwd,
    database = dbname
)
cur = db.cursor()
cur.execute("select * from tests")
tests_dat = cur.fetchall()
cur.exceute("show columns from tests")
tests_col = cur.fetchall()
cur.execute("select * from topics")
topics_dat = cur.fetchall()
cur.execute("show columns from topics")
topics_col = cur.fetchall()
cur.execute("select * from questions")
qs_dat = cur.fetchall()
cur.execute("show columns from questions")
qs_col = cur.fetchall()
cur.close()
db.close()

def create_df(dat, col):
    df = pd.DataFrame(dat, columns=[i[0] for i in col])
    return df.copy()

tests_df = create_df(tests_dat, tests_col)
topics_df = create_df(topics_dat, topics_col)
qs_df = create_df(qs_dat, qs_col)

# w-flow: tests_per week user 
# w-flow: topics per week user 

st.write(tests_df)
st.write(topics_df)
st.write(qs_df)
