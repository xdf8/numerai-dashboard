import datetime as dt
import streamlit as st

import pandas as pd
import numpy as np

import numerapi

import plotly.express as px

# setup backend
napi = numerapi.SignalsAPI()
MODELS_TO_CHECK = leaderboard_df = pd.DataFrame(napi.get_leaderboard(limit = 10_000))
MODELS_TO_CHECK = leaderboard_df['username'].sort_values().to_list()
DEFAULT_MODELS = ['kenfus', 'kenfus_drop']
ROUNDS_TO_SHOW = 20


# setup website
st.set_page_config(page_title = 'Numerai Dashboard')
st.title('Numerai Dashboard')
st.write(
    '''
    The Numerai Tournament is where you build machine learning models on abstract financial data to predict the stock market. Your models can be staked with the NMR cryptocurrency to earn rewards based on performance.
    '''
)
st.header('Scoring')
st.write(
    '''
    You are primarily scored on the correlation (`corr`) between your predictions and the targets. 
    You are also scored on `mmc`. The higher the correlation the better for both.
    '''
)
st.subheader('MMC')
st.write(
    '''
    Each user is incentivized to maximize their individual correlation score. But Numerai wants to maximize the meta model's correlation score, where the meta model is the stake weighted ensemble of all submissions.
    Meta model contribution `mmc` is designed to bridge this gap. Whereas correlation rewards individual performance, `mmc` rewards contribution to the meta model's correlation or group performance.
    '''
)
## Reputation
st.header('Reputation')
st.subheader('Motivation')
st.write(
    '''
    Long term performance is key.
    While your payouts depend on your performance in a single round, your reputation and rank depends on your performance over 20 rounds.
    '''
)
st.subheader('Calculation')
st.write(
    '''
    Your reputation for `corr` and `mmc` on round n is a weighted average of that metric over the past 20 rounds including rounds that are currently resolving.
    '''
)


with st.sidebar:
    st.header('Settings')
    st.write('# Graphs')
    hover_mode = st.checkbox('Detailed hover mode')

    selected_models = st.multiselect(
        'Select models for reputation analysis:', 
        MODELS_TO_CHECK,
        DEFAULT_MODELS
    )
    st.write('# Returns')
    cum_corr = st.checkbox('Cumulative returns')
    corr_multi = st.selectbox(
        'Select multiplier for correlation', 
        [0.5, 1, 2],
        2,
    )

    mmc_multi = st.selectbox(
        'Select multiplier for MMC', 
        [0.5, 1, 2, 3],
        3
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
st.header('Returns')
st.subheader('MMC & Correlation')
st.write(
    '''
    For MMC and Correlation we can select a multiplier to calculate our returns for that specific round. The correlation or MMC is then multiplied by the selected number.
    - For Correlation, we can select between  `0.5`, `1` and `2`.
    - For MMC, we can select between `0`, `0.5`, `1`, `2` and `3`.
    '''
    )
st.subheader('Example')
st.write(
    '''
    We have archieved a correlation and MMC of 0.05 this round and have selected the highest multiplier for both: `0.05 * 2 + 0.05 * 3 = 0.25`. 
    
    Thus, our return for this week is 25%.
    '''
)

st.subheader('Graphs')
score_dfs = []

for model in selected_models:
    df_model_score = pd.DataFrame(napi.daily_submissions_performances(model))
    df_model_score = df_model_score.dropna(subset=['date'])
    df_model_score = df_model_score.sort_values(['date', 'roundNumber'], ascending = True)
    df_model_score = df_model_score.groupby('roundNumber').last().reset_index()[['roundNumber', 'date', 'correlation', 'mmc']]
    df_model_score['returns'] = corr_multi * df_model_score['correlation'] + mmc_multi*df_model_score['mmc']
    df_model_score['model'] = model

    if not df_model_score.empty:
        df_model_score['model'] = model
        score_dfs.append(df_model_score)

score_dfs = pd.concat(score_dfs)

round_start_calc = st.slider(
    'Select starting round to calculate returns.', 
    int(score_dfs['roundNumber'].min()),
    int(score_dfs['roundNumber'].max())
)

score_dfs = score_dfs[score_dfs['roundNumber']>=round_start_calc]

score_dfs['corr_cumsum'] = score_dfs.groupby(['model'])['correlation'].cumsum()
score_dfs['mmc_cumsum'] = score_dfs.groupby(['model'])['mmc'].cumsum()
score_dfs['returns_cumsum'] = score_dfs.groupby(['model'])['returns'].cumsum()

returns_plot = px.line(
    score_dfs, 
    x = 'roundNumber',  
    y = 'returns_cumsum' if cum_corr else 'returns',
    color = 'model', 
    title = f'{"Cumulative r" if cum_corr else "R"}eturns after round {round_start_calc}'
)

corr_score_plot = px.line(
    score_dfs, 
    x = 'roundNumber',  
    y = 'corr_cumsum' if cum_corr else 'correlation',
    color = 'model', 
    title = f'{"Cumulative c" if cum_corr else "C"}orrelation after round {round_start_calc}'
)

mmc_score_plot = px.line(
    score_dfs, 
    x = 'roundNumber',  
    y = 'mmc_cumsum' if cum_corr else 'mmc',
    color = 'model', 
    title = f'{"Cumulative " if cum_corr else ""}MMC after round {round_start_calc}'
)

st.plotly_chart(returns_plot)
st.plotly_chart(corr_score_plot)
st.plotly_chart(mmc_score_plot)