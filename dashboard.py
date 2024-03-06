import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from statsmodels.tsa.seasonal import STL
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_sharing_df(df):
    daily_sharing_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    })
    daily_sharing_df = daily_sharing_df.reset_index()
    daily_sharing_df.rename(columns={
        "cnt": "total_bicycle"
    }, inplace=True)
    
    return daily_sharing_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season")["cnt"].sum().reset_index()
    byseason_df.rename(columns={
        "cnt": "total_bicycle"
    }, inplace=True)
    
    return byseason_df

def create_bymonth2011_df(df):
    bymonth2011_df = df[df['yr'] == '2011'].groupby(by=["yr", "mnth"])["total hours"].sum().reset_index()
    bymonth2011_df.rename(columns={
        "total hours": "total_hours"
    }, inplace=True)
    
    return bymonth2011_df

def create_bymonth2012_df(df):
    bymonth2012_df = df[df['yr'] == '2012'].groupby(by=["yr", "mnth"])["total hours"].sum().reset_index()
    bymonth2012_df.rename(columns={
        "total hours": "total_hours"
    }, inplace=True)
    
    return bymonth2012_df

def creat_stl_decomposition(col1, col_name, seasonal_period):
    data_stl = pd.read_csv('..\Proyek Analisis Data\day.csv', parse_dates=[col1], index_col= col1)
    time_series_data = data_stl[col_name]

    decomposition = STL(time_series_data, seasonal= seasonal_period).fit()
    trend, seasonal, residual = decomposition.trend, decomposition.seasonal, decomposition.resid

    stl_df = pd.DataFrame({
        'time': data_stl.index,
        'trend': trend,
        'seasonal': seasonal,
        'residual': residual
    })

    return stl_df

day_df = pd.read_csv("..\Proyek Analisis Data\day.csv")
hour_df = pd.read_csv("..\Proyek Analisis Data\hour.csv")

datetime_column = ["dteday"]
 
for column in datetime_column:
  day_df[column] = pd.to_datetime(day_df[column])

hour_df['dteday'] = hour_df['dteday'].astype('category')

hour_df['total hours']= hour_df["hr"] * hour_df["cnt"]

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

season_name = {1: 'springer', 2: 'summer', 3: 'fall', 4: 'winter'}
day_df['season'] = day_df['season'].replace(season_name)

month_name = {1: 'Jan', 2: 'Feb', 3: 'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}
hour_df['mnth'] = hour_df['mnth'].replace(month_name)

year_name = {0: '2011', 1: '2012'}
hour_df['yr'] = hour_df['yr'].replace(year_name)

with st.sidebar:
    st.image("D:\Bangkit\Tugas\Dicoding\Analisis Data Dengan Python\bikesharing.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

daymain_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

daily_sharing_df = create_daily_sharing_df(daymain_df)
byseason_df = create_byseason_df(day_df)
bymonth2011_df= create_bymonth2011_df(hour_df)
bymonth2012_df= create_bymonth2012_df(hour_df)
stl_df = creat_stl_decomposition('dteday', 'cnt', 31 )

month_order = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August', 'Sept', 'Oct', 'Nov', 'Dec']

bymonth2011_df['mnth'] = pd.Categorical(bymonth2011_df['mnth'], categories=month_order, ordered=True)
bymonth2011_df = bymonth2011_df.sort_values('mnth')

bymonth2012_df['mnth'] = pd.Categorical(bymonth2012_df['mnth'], categories=month_order, ordered=True)
bymonth2012_df = bymonth2012_df.sort_values('mnth')
st.header('Bike Sharing Dashboard :sparkles:')

st.subheader('Daily Sharing')
 
col1, col2 = st.columns(2)
 
with col1:
    total_sharing = daily_sharing_df.total_bicycle.sum()
    st.metric("Total Sharing", value= total_sharing)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daymain_df["dteday"],
    daily_sharing_df["total_bicycle"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Best & Worst Performing Season")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors1 = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="season", y="total_bicycle", data=byseason_df.head(4), palette=colors1, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Season", fontsize=30)
ax[0].set_title("Best Performing Season", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

colors2 = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3"]
sns.barplot(x="season", y="total_bicycle", data=byseason_df.sort_values(by="season", ascending=True).head(4), palette=colors2, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Season", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Season", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.title('Total Hours per Month')
tab1, tab2, tab3 = st.tabs(["2011", "2012", "2011 & 2012"])

with tab1:    
    fig, ax = plt.subplots()
    ax.plot(bymonth2011_df['mnth'], bymonth2011_df['total_hours'], marker='o', linewidth= 2, color='b')

    ax.set_xlabel('Month')
    ax.set_ylabel('Total Hours')
    ax.set_title('Total Hours per Month (2011)')

    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots()
    ax.plot(bymonth2012_df['mnth'], bymonth2012_df['total_hours'], marker='o', linewidth= 2, color='#Ff0000')

    ax.set_xlabel('Month')
    ax.set_ylabel('Total Hours')
    ax.set_title('Total Hours per Month (2012)')

    st.pyplot(fig)

with tab3:

    fig, ax = plt.subplots()

    ax.plot(bymonth2011_df['mnth'], bymonth2011_df['total_hours'], marker='o', linewidth=2, color='b', label='2011')
    ax.plot(bymonth2012_df['mnth'], bymonth2012_df['total_hours'], marker='o', linewidth=2, color='#FF0000', label='2012')

    ax.set_xlabel('Month')
    ax.set_ylabel('Total Hours')
    ax.set_title('Total Hours per Month (2011-2012)')
    ax.legend()

    st.pyplot(fig)


st.title('Trend, Seasonal, dan Residual dari STL Decomposition')
fig, ax = plt.subplots(figsize=(12, 8))

ax.plot(stl_df['time'], stl_df['trend'], label='Trend', linewidth=2)
ax.plot(stl_df['time'], stl_df['seasonal'], label='Seasonal', alpha=0.8)

ax.plot(stl_df['time'], stl_df['residual'], label='Residual', alpha=0.5)

ax.legend()
ax.set_title('Trend, Seasonal, dan Residual dari STL Decomposition')
ax.set_xlabel('Time')
ax.set_ylabel('Value')

st.pyplot(fig)

st.caption('Copyright (c) Elin 2024')