import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import json
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import subprocess

st.title("My Dashboard")

# scrape and load data
@st.cache(allow_output_mutation=True)
def load_data():
    # scrape covid data
    ds_url = 'https://www.data.gv.at/katalog/dataset/846448a5-a26e-4297-ac08-ad7040af20f1'
    page = requests.get(ds_url).text
    soup = BeautifulSoup(page, 'html.parser')
    file_url = soup.find('a', class_='resource-url-analytics').get('href')
    #req = requests.get(file_url)
    #print(req)
    #df = pd.read_csv(req.content, sep=";")
    df = pd.read_csv(file_url, sep=";")
    df['Meldedatum'] = pd.to_datetime(df['Meldedatum'], format = '%d.%m.%Y %H:%M:%S').dt.date
    return df

# filter 1
def filter_by_date(data):
    start = st.sidebar.date_input('Start Meldedatum', data['Meldedatum'].agg('min'))
    end = st.sidebar.date_input('Ende Meldedatum', data['Meldedatum'].agg('max'))
    if (start, end):
        return data[data["Meldedatum"].between(start, end)]
    return data

# filter 2
def filter_by_state(data):
    state = st.sidebar.selectbox(
        'Bundesland',
        [''] + list(data['Bundesland'].drop_duplicates().sort_values())
    )
    if state:
        return data[data['Bundesland']==state]
    return data

# change css
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://www.kibrispdr.org/data/11/background-hitam-metalik-58.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()
df = load_data()

# sidebar
st.sidebar.title("Filter")
df = filter_by_date(df)
df = filter_by_state(df)

# get values for api-call
x = int(len(df))
y = int(df['TestGesamt'].agg('max'))

st.sidebar.title("Calculate mean via FastAPI")
st.sidebar.write('Anzahl Tage: ' + str(x))
st.sidebar.write('TestGesamt Summe: ' + str(y))


#create needed data subset
df_plot_1 = (df
                .filter(['Meldedatum','Bundesland','TestGesamt'])
                .groupby(['Meldedatum','Bundesland'])
                .agg('sum')
                .reset_index()
                )

#configure plot
plot_1 = plt.figure(figsize=(20,10))
plt.style.use('seaborn-darkgrid')
sns.lineplot(data = df_plot_1
             ,x = 'Meldedatum'
             ,y = 'TestGesamt'
             ,hue = 'Bundesland'
             ).set_title('TestGesamt x Bundesland Verlauf', fontsize=20)

st.pyplot(plot_1)

#create needed data subset
df_plot_2 = (df
                .filter(['Bundesland','TestGesamt'])
                .groupby('Bundesland')
                .agg('sum')
                .reset_index()
                )

#configure plot
plot_2 = plt.figure(figsize=(20,10))
plt.style.use('seaborn-darkgrid')
sns.barplot(data = df_plot_2.sort_values('TestGesamt', ascending=False)
             ,x = 'TestGesamt'
             ,y = 'Bundesland'
             ).set_title('TestGesamt x Bundesland Gesamt', fontsize=20)
st.pyplot(plot_2)


# show dataframe
st.dataframe(df_plot_1)

# generate input for api-call
inputs = {"x": x, "y": y}

if st.sidebar.button('Calculate!'):
    res = requests.post(url = "http://sdc_4:8000/calculateMean", data = json.dumps(inputs))

    st.sidebar.subheader(f"API response:\nTestGesamt Mean = {res.text}")

subprocess.Popen(["uvicorn", "--host", "0.0.0.0", "FastAPI:app"])
