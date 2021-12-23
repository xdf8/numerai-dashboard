import datetime as dt
import streamlit as st

import pandas as pd
import numpy as np

import numerapi

import plotly.express as px

# setup backend
#napi = numerapi.SignalsAPI(secret_key = "JJWK2ZWDRU3IGE55U33ZHRN6SDRDDP25KAFP66NULNU6JFEQH776MS4FLCE5GRA4", public_id = "MSDMKBBMHC4O2H6IT64VNRXMA3JYRAFJ")
napi = numerapi.SignalsAPI()
MODELS_TO_CHECK = leaderboard_df = pd.DataFrame(napi.get_leaderboard(limit = 10_000))
MODELS_TO_CHECK = leaderboard_df['username'].sort_values().to_list()
DEFAULT_MODELS = ['kenfus', 'kenfus_drop']
ROUNDS_TO_SHOW = 20


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


with st.sidebar:
    st.header('Global Settings')
    st.write('Graphs')
    hover_mode = st.checkbox('Detailed hover mode')

    selected_models = st.multiselect(
        'Select models for reputation analysis:', 
        MODELS_TO_CHECK,
        DEFAULT_MODELS
    )

    

rep_dfs = []

for model in selected_models:
    df_model_rank_rep = pd.DataFrame(napi.daily_model_performances(model))
    df_model_rank_rep['model'] = model
    #df_model_rank_rep.sort_values('')
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


# Correlation over time

st.header('Model Scores')

score_dfs = []

for model in selected_models:
    df_model_score = pd.DataFrame(napi.daily_submissions_performances(model))
    df_model_score = df_model_score.dropna(subset=['date'])
    df_model_score = df_model_score.sort_values(['date', 'roundNumber'], ascending = True)
    df_model_score = df_model_score.groupby('roundNumber').last().reset_index()[['roundNumber', 'date', 'correlation', 'mmc']]
    df_model_score['corr_cumsum'] = df_model_score['correlation'].cumsum()
    df_model_score['mmc_cumsum'] = df_model_score['mmc'].cumsum()
    df_model_score['model'] = model

    if not df_model_score.empty:
        df_model_score['model'] = model
        score_dfs.append(df_model_score)

score_dfs = pd.concat(score_dfs)
#daily_dfs = daily_dfs.dropna(axis=1, how='all')
cum_corr = st.checkbox('Cumulative correlation')

if not cum_corr:
    corr_score_plot = px.line(
        score_dfs, 
        x = 'roundNumber',  
        y = 'correlation',
        color = 'model', 
        title = f'Correlation in round {69}'
    )

else:
    corr_score_plot = px.line(
        score_dfs, 
        x = 'roundNumber',  
        y = 'corr_cumsum',
        color = 'model', 
        title = f'Correlation in round {69}'
    )

if not cum_corr:
    mmc_score_plot = px.line(
        score_dfs, 
        x = 'roundNumber',  
        y = 'mmc',
        color = 'model', 
        title = f'Correlation in round {69}'
    )

else:
    mmc_score_plot = px.line(
        score_dfs, 
        x = 'roundNumber',  
        y = 'mmc_cumsum',
        color = 'model', 
        title = f'Correlation in round {69}'
    )

st.plotly_chart(corr_score_plot)
st.plotly_chart(mmc_score_plot)