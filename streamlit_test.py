import streamlit as st

import pandas as pd
import numpy as np

import numerapi

import plotly.express as px

st.set_page_config(page_title = 'Numerai Dashboard')

st.title('Numerai Dashboard')

st.header('Reputation')

#st.metric('ayylmao', 69, 42)

# some API calls do not require logging in
public_id = "AVLW3M6UOZG3EIYLNN3JGUYHHC5MHV43"
secret_key = "RSZTLYGVX4EICEDQFCMBKVS3MPPCZ6UT56ZMGAVD64DQEZRMAXNZIDBA6EW3XJTQ"
napi = numerapi.NumerAPI(public_id, secret_key)

# get competitions
#all_competitions = napi.get_competitions()

model_list = [
    'xdf8_0',
    'xdf8_2',
    'kenfus_1'
]

with st.sidebar:
    st.sidebar.write('# Select your Model')
    selected_models = st.multiselect(
        'Select your Model', 
        [
            'xdf8_0',
            'xdf8_2',
            'kenfus_1',
            'kenfus_3', 
            'kenfus_2', 
            'kenfus_4',
            'kenfus'
        ],
        'xdf8_0'
    )

# check submission status
model_id = napi.get_models()[selected_model]
napi.submission_status(model_id)

# convert results to a pandas dataframe
# reverse dataframe and drop old index
df_model_rank_rep = pd.DataFrame(napi.daily_model_performances(selected_model)).iloc[::-1].reset_index(drop = True)

st.table(df_model_rank_rep.head())

# built and display reputation plot

model_rep_metrics = st.multiselect(
        'Metrics', 
        [
            'corrRep', 
            'mmcRep'
            ], 
        'corrRep'
    )

rep_plot = px.line(df_model_rank_rep, x = 'date', y = model_rep_metrics, title = 'Model Reputation over time')

st.plotly_chart(rep_plot)


# built and display rank plot

model_rank_metrics = st.multiselect('Metrics', ['corrRank', 'mmcRank'], 'corrRank')

## scale y-axis
min_rank = np.minimum(df_model_rank_rep['corrRank'], df_model_rank_rep['mmcRank'])

rank_plot = px.line(
    df_model_rank_rep,
     x = 'date', 
     y = model_rank_metrics, 
     title = 'Model Rank over time',
     range_y = [0, min_rank])
rank_plot['layout']['yaxis']['autorange'] = 'reversed'


st.plotly_chart(rank_plot)

model_id = napi.get_models()[selected_model]
napi.submission_status(model_id)