import streamlit as st 
import mysql.connector as conn
import pandas as pd 
import datetime as dt
import matplotlib.pyplot as plt
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
cur.execute("show columns from tests")
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

# w-flow: score user for consistancy
sorted_test_df = tests_df.sort_values(by=["test_date"])
sorted_test_df["test_date"] = sorted_test_df["test_date"].dt.date
sco_date_wise= sorted_test_df.groupby(["test_date"],as_index=False)["score"].sum()
start_date = sorted_test_df["test_date"].min()
end_date = sorted_test_df["test_date"].max()
inconsistant_days = (end_date - start_date).days - sco_date_wise[sco_date_wise["score"]!=0].count().shape[0]
st.write(inconsistant_days)

# check if the user was consistant for last 5 days in row 
df_last_5 = pd.DataFrame({"dates": pd.date_range(start_date, end_date, freq='D')})
print(df_last_5)


# w-flow: tests_per week user 
# //print(tests_df.info())
test_per_week = tests_df.groupby(pd.Grouper(key='test_date', freq='1W')).count()
test_per_week.reset_index(inplace=True)
test_per_week["test_date"] = pd.to_datetime(test_per_week["test_date"])
st.header("test per week user")
# //st.write(test_per_week)
# //print(test_per_week.info())
fig = plt.figure(figsize=(10, 10))
ax = fig.subplots(2,2, sharey='all', sharex='all')
ax[0,0].step(test_per_week["test_date"], test_per_week["test_id"])
ax[0,0].set_ylabel("Number of tests")
ax[0,0].set_xlabel("Date")
for i, label in enumerate(test_per_week["test_id"]):
    ax[0,0].annotate(str(label), (test_per_week["test_date"][i]+pd.Timedelta(hours=3), test_per_week["test_id"][i]))
ax[0,1].step(test_per_week["test_date"], test_per_week["easy_Questions"])
ax[0,1].set_ylabel("Number of easy questions")
ax[0,1].set_xlabel("Date")
for i, label in enumerate(test_per_week["easy_Questions"]):
    ax[0,1].annotate(str(label), (test_per_week["test_date"][i]+pd.Timedelta(hours=3), test_per_week["easy_Questions"][i]))
ax[1,0].step(test_per_week["test_date"], test_per_week["medium_Questions"])
ax[1,0].set_ylabel("Number of medium questions")
ax[1,0].set_xlabel("Date")
for tik in ax[1,0].get_xticklabels():
    tik.set_rotation(45)
for i, label in enumerate(test_per_week["medium_Questions"]):
    ax[1,0].annotate(str(label), (test_per_week["test_date"][i]+pd.Timedelta(hours=3), test_per_week["medium_Questions"][i]))
ax[1,1].step(test_per_week["test_date"], test_per_week["difficult_Questions"])
ax[1,1].set_ylabel("Number of difficult questions")
ax[1,1].set_xlabel("Date")
for i, label in enumerate(test_per_week["difficult_Questions"]):
    ax[1,1].annotate(str(label), (test_per_week["test_date"][i]+pd.Timedelta(hours=3), test_per_week["difficult_Questions"][i]))
for tik in ax[1,1].get_xticklabels():
    tik.set_rotation(45)
fig.align_xlabels()
st.pyplot(fig)


# w-flow: scores per week user
Score_avg_per_week2 = tests_df.groupby(pd.Grouper(key='test_date', freq='1W'))["score"].mean()
Score_avg_per_week = Score_avg_per_week2.reset_index()
Score_avg_per_week["test_date"] = pd.to_datetime(Score_avg_per_week["test_date"])
st.header("Score avg per week user")
st.write(Score_avg_per_week)
fig2 = plt.figure(figsize=(5, 5))
ax= fig2.subplots()
ax.bar(x=Score_avg_per_week["test_date"], height=Score_avg_per_week["score"])
ax.set_xlabel("Date")
ax.set_ylabel("Score")
for i, lab in enumerate(Score_avg_per_week["score"]):
    ax.annotate(str(round(lab,2)), (Score_avg_per_week["test_date"][i]-pd.Timedelta(hours=8), Score_avg_per_week["score"][i]))
for tik in ax.get_xticklabels():
    tik.set_rotation(75)
st.pyplot(fig2)



# w-flow: sum of scores per day user
test_df_copy = tests_df.copy()
test_df_copy["test_date"] = tests_df["test_date"].dt.date
sco_sum_by_day = test_df_copy.groupby(["test_date"])["score"].sum()
sco_sum_by_day = sco_sum_by_day.reset_index()
sco_sum_by_day["test_date"] = pd.to_datetime(sco_sum_by_day["test_date"])
st.header("Score sum per day user")
st.write(sco_sum_by_day)
fig3 = plt.figure(figsize=(15, 5))
ax= fig3.subplots()
ax.bar(x=sco_sum_by_day["test_date"], height=sco_sum_by_day["score"])
ax.set_xlabel("Date")
ax.set_ylabel("Score")
for i, lab in enumerate(sco_sum_by_day["score"]):
    ax.annotate(str(round(lab,2)), (sco_sum_by_day["test_date"][i]-pd.Timedelta(hours=8), sco_sum_by_day["score"][i]))
for tik in ax.get_xticklabels():
    tik.set_rotation(75)
st.pyplot(fig3)

# w-flow: topics per week user 
tp_per_wk = topics_df.copy()
tp_per_wk["topic_start_date"] = topics_df["topic_start_date"].dt.date
tp_per_wk = topics_df.groupby([pd.Grouper(key='topic_start_date', freq='1W'),"topic_type"]).count()
tp_per_wk_rs_ind = tp_per_wk.reset_index()

plt_sk = tp_per_wk["topic_id"].unstack(fill_value=0)

st.line_chart(plt_sk, x_label="Date", y_label="Number of Topics", use_container_width=True)

st.write(sco_sum_by_day.tail())
if sco_sum_by_day["score"].sum() > 0:
    st.header("Your total consistancy score is: ")
    st.write(sco_sum_by_day["score"].sum())
else:
    sc_0 =sco_sum_by_day[sco_sum_by_day["score"] == 0].count()
    st.header("Your total consistancy score is: ")
    st.write(sco_sum_by_day["score"].sum()-sc_0["score"])
    st.write("to remove debuff you will have to be consistant for 7 days in a row")
# // st.write(tests_df)
# // st.write(topics_df)
# // st.write(qs_df)
# // 