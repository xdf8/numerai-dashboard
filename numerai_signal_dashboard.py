import datetime as dt
import streamlit as st

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import numerapi

import plotly.express as px

from utils import *




# setup backend
napi = numerapi.SignalsAPI()
leaderboard_df = pd.DataFrame(napi.get_leaderboard(limit = 10_000))
MODELS_TO_CHECK = leaderboard_df['username'].sort_values().to_list()
DEFAULT_MODELS = [
    'kenfus', 
    'kenfus_drop', 
    'kenfus_t_500', 
    'kenfus_t_600', 
    'kenfus_t_600_drop', 
    'kenfus_t_900', 
    'kenfus_t_ensemble_1', 
    'kenfus_t_700', 
    'kenfus_t_800',
    'kenfus_1_528',
    'kenfus_frac_diff',
    'kenfus_1_528_drop'
    ]
ROUNDS_TO_SHOW = 20


# setup website
st.set_page_config(page_title = 'Numerai Dashboard')
st.title('Numerai Dashboard')
st.write(
    '''
    The Numerai Tournament is where you build machine learning models on abstract financial data to predict the stock market. Your models can be staked with the NMR cryptocurrency to earn rewards based on performance.
    '''
)
st.subheader('Motivation')
st.write(
    '''
    To decide which model is best, you need to compare them on different criteria. On the [official leaderboard](https://signals.numer.ai/tournament), this is difficult to do.
    '''
)
st.header('Scoring')
st.write(
    '''
    You are primarily scored on the correlation `corr` between your predictions and the targets. 
    You are also scored on meta model contribution `mmc`. The higher the better.
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

    show_only_resolved_rounds = st.checkbox('Show only resolved rounds')

    selected_models = st.multiselect(
        'Select models for reputation analysis:', 
        MODELS_TO_CHECK,
        DEFAULT_MODELS
    )
    st.write('# Returns')
    cum_corr = st.checkbox('Cumulative returns', value=True)
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
    - For Correlation, the multiplier is currently fixed at `2`.
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
    df_model_score['returns'] = 2 * df_model_score['correlation'] + mmc_multi*df_model_score['mmc']
    df_model_score['model'] = model


    if not df_model_score.empty:
        df_model_score['model'] = model
        score_dfs.append(df_model_score)

# Get lastest resolved round: 
RESOLVED_ROUND_MODEL = 'apprentice_key'
cnapi = CustomNumerAPI()
try:
    round_status = pd.DataFrame(cnapi.get_round_performances(RESOLVED_ROUND_MODEL)).set_index("roundNumber")
    last_resolved_round = round_status[round_status.roundResolved==True].index.max()
except TypeError as E:
    # Catch when numerais API is down (happens sometimes) and approximate it
    round_numbers = np.unique(df_model_score.roundNumber)
    last_resolved_round = round_numbers[-5]
    

score_dfs = pd.concat(score_dfs)

if show_only_resolved_rounds:
    score_dfs = score_dfs[score_dfs.roundNumber <= last_resolved_round]

round_start_calc = st.slider(
    'Select starting round to calculate returns.', 
    int(score_dfs['roundNumber'].min()),
    int(score_dfs['roundNumber'].max())
)

score_dfs = score_dfs[score_dfs['roundNumber']>=round_start_calc]

score_dfs['corr_cumsum'] = score_dfs.groupby(['model'])['correlation'].cumsum()
score_dfs['mmc_cumsum'] = score_dfs.groupby(['model'])['mmc'].cumsum()
score_dfs['returns_cumsum'] = score_dfs.groupby(['model'])['returns'].cumsum()
score_dfs['returns_corr'] = 2 * score_dfs['corr_cumsum']
score_dfs['returns_mmc'] = mmc_multi * score_dfs['mmc_cumsum']


returns_plot = px.line(
    score_dfs, 
    x = 'roundNumber',  
    y = 'returns_cumsum' if cum_corr else 'returns',
    color = 'model'
)

corr_score_plot = px.line(
    score_dfs, 
    x = 'roundNumber',  
    y = 'corr_cumsum' if cum_corr else 'correlation',
    color = 'model'
)

mmc_score_plot = px.line(
    score_dfs, 
    x = 'roundNumber',  
    y = 'mmc_cumsum' if cum_corr else 'mmc',
    color = 'model'
)

# Bar plot
colors = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]
colors = 5*colors


melted = score_dfs.melt(id_vars=['roundNumber', 'model', 'date'])
melted = melted[melted.variable.isin(['mmc', 'correlation'])]
melted['color_idx'] = melted.groupby(['model', 'variable']).ngroup()
melted['color'] = melted['color_idx'].apply(lambda x: colors[x])

# Current returns
corr_mmc_bar = go.Figure()
for i, model in enumerate(selected_models):
    melted_tmp = melted[melted.model==model]
    corr_mmc_bar.add_trace(
        go.Bar(
        x=melted_tmp.roundNumber,
        y=melted_tmp.value,
        text=melted_tmp.variable,
        name=model,
        textposition='none',
        marker_color=melted_tmp.color
        )
    )

# Cummulative returns
curr_returns_df = score_dfs.groupby('model').tail(1)
curr_returns_plot = px.bar(curr_returns_df, x="model", y=["returns_corr", "returns_mmc"])

# Plots
st.subheader(f'Cumulative returns per Model')
st.plotly_chart(curr_returns_plot)

st.subheader(f'Correlation and MMC per Round per Model')
st.plotly_chart(corr_mmc_bar)

st.subheader(f'{"Cumulative r" if cum_corr else "R"}eturns after round {round_start_calc}')
st.plotly_chart(returns_plot)

st.subheader(f'{"Cumulative c" if cum_corr else "C"}orrelation after round {round_start_calc}')
st.plotly_chart(corr_score_plot)

st.subheader(f'{"Cumulative " if cum_corr else ""}MMC after round {round_start_calc}')
st.plotly_chart(mmc_score_plot)
