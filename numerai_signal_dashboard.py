import datetime as dt
import streamlit as st

import pandas as pd
import numpy as np

import numerapi

import plotly.express as px

# setup backend
#napi = numerapi.SignalsAPI(secret_key = "JJWK2ZWDRU3IGE55U33ZHRN6SDRDDP25KAFP66NULNU6JFEQH776MS4FLCE5GRA4", public_id = "MSDMKBBMHC4O2H6IT64VNRXMA3JYRAFJ")
napi = numerapi.SignalsAPI()

# setup website
st.set_page_config(page_title = 'Numerai Dashboard')
st.title('Numerai Dashboard')

## Reputation
st.header('Reputation')

st.write(
    '''
    The reputation is the weighted average of correlation over the previous 20 rounds.
    The plots are interactive, which means you can:
    - zoom
    - scroll
    - hover over datapoints to get more information
    - ADD MORE
    '''
)

leaderboard_df = pd.DataFrame(napi.get_leaderboard(limit = 10_000))
model_list = leaderboard_df['username'].sort_values().to_list()

with st.sidebar:
    st.header('Global Settings')
    st.write('Graphs')
    hover_mode = st.checkbox('Detailed hover mode')

    selected_models_rep = st.multiselect(
        'Select models for reputation analysis:', 
        model_list,
        ['kenfus', 'kenfus_drop']
    )

rep_dfs = []

for model in selected_models_rep:
    df_model_rank_rep = pd.DataFrame(napi.daily_model_performances(model))
    df_model_rank_rep['model'] = model
    rep_dfs.append(df_model_rank_rep)

rep_dfs = pd.concat(rep_dfs)

## Correlation Reputation
st.write('### Correlation Reputation')

corr_rep_plot = px.line(
    rep_dfs, 
    x = 'date',  
    y = 'corrRep',
    color = 'model', 
    title = 'Correlation reputation over time'
)

if hover_mode:
    corr_rep_plot.update_layout(hovermode = 'x')

corr_rep_plot.update_layout(
    xaxis = dict(
        rangeselector = dict(
            buttons = list([
                dict(count = 7,
                     label = "1w",
                     step = "day",
                     stepmode = "backward"),
                dict(count = 1,
                     label = "1m",
                     step = "month",
                     stepmode = "backward"),
                dict(step = "all")
            ]),
            bgcolor = 'black'
        )
    )
)

st.plotly_chart(corr_rep_plot)

## MMC Reputation
st.write('### MMC Reputation')

mmc_rep_plot = px.line(
    rep_dfs, 
    x = 'date',  
    y = 'corrRep',
    color = 'model', 
    title = 'MMC reputation over time'
)

if hover_mode:
    mmc_rep_plot.update_layout(hovermode = 'x')

mmc_rep_plot.update_layout(
    xaxis = dict(
        rangeselector = dict(
            buttons = list([
                dict(count = 7,
                     label = "1w",
                     step = "day",
                     stepmode = "backward"),
                dict(count = 1,
                     label = "1m",
                     step = "month",
                     stepmode = "backward"),
                dict(step = "all")
            ]),
            bgcolor = 'black'
        )
    )
)

st.plotly_chart(mmc_rep_plot)


# COMPARE MULTIPLE MODELS OVER ONE ROUND
st.header('Daily Scores')

selected_models_daily = st.multiselect(
    'Select models for daily score analysis:', 
    [
        'xdf8_0',
        'xdf8_2',
        'kenfus_1',
        'kenfus_3', 
        'kenfus_2', 
        'kenfus_4',
        'kenfus'
    ],
    ['xdf8_0', 'xdf8_2', 'kenfus']
)

daily_dfs = []

for model in selected_models_daily:
    df_model_daily = pd.DataFrame(napi.daily_submissions_performances(model))
    df_model_daily['model'] = model
    daily_dfs.append(df_model_daily)

daily_dfs = pd.concat(daily_dfs).sort_values('date')

selected_round_daily = st.selectbox('Select round:', daily_dfs['roundNumber'].unique())

st.dataframe(daily_dfs[daily_dfs['roundNumber'] == selected_round_daily])

daily_score_plot = px.line(
    daily_dfs[daily_dfs['roundNumber'] == selected_round_daily], 
    x = 'date',  
    y = 'correlation',
    color = 'model', 
    title = f'Correlation in round {selected_round_daily}'
)

if hover_mode:
    daily_score_plot.update_layout(hovermode = 'x')

# USE THIS FOR COMPARING ONE MODEL BUT MULTIPLE ROUNDS

min_date = daily_dfs[daily_dfs['roundNumber'] == selected_round_daily]['date'].min()
max_date = daily_dfs[daily_dfs['roundNumber'] == selected_round_daily]['date'].max()
delta_days = (max_date - min_date).days

daily_score_plot.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count = delta_days,
                     label = "round",
                     step = "day",
                     stepmode = "backward"),
                dict(count = 7,
                     label = "1 week",
                     step = "day",
                     stepmode = "backward")
            ]),
            bgcolor = 'black'
        )
    )
)

st.plotly_chart(daily_score_plot)