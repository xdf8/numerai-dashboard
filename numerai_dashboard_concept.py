import streamlit as st

import pandas as pd
import numpy as np

import plotly.express as px

# setup backend

# setup website
st.set_page_config(page_title = 'dko Concept')
st.title('Concept: Numerai Dashboard')

## Reputation
st.header('Explanation: what is numerai?')

st.write(
    '''
    Here we're going to explain the basics of the numerai tournament and what we're going with this webite.
    '''
)


with st.sidebar:
    st.header('Sidebar')
    st.write('Settings and Selctions go here.')
    st.write(
        '''
        There are different ways to select data: 
        - Checkbox
        - Multiselect
        - Dropdowns

        Possible selections: model, metric, timeframe, round, etc.
        '''
        )

    example_checkbox = st.checkbox('This is a checkbox')
    
    example_multi = st.multiselect(
        'This is a multiselect',
        [
            'these',
            'are',
            'the',
            'possible',
            'selections'
        ],
        [
            'these',
            'are',
            'the',
            'possible',
            'selections'
        ]
    )

    st.selectbox('This is a selectbox', ['select', 'some', 'value'])



st.write(
    '''
    ### Correlation Reputation
    The main component of the website/analysis are going to be plots. 
    They're going to be interactive, which means you can zoom, select a specific area, 
    change the axis, save the plot to disk and much more.
    '''
    )


example_multi = st.multiselect(
        'All selections can also be done inline',
        [
            'for',
            'example',
            'this',
            'multiselect'
        ],
        [
            'for',
            'example',
            'this',
            'multiselect'
        ]
    )

example_x = np.arange(0, 100, 1)
example_y = np.random.normal(0, 1, 100)

st.write('## Example plot')
example_plot = px.line(
    x = example_x, 
    y = example_y,
    title = 'Example plot'
)
st.plotly_chart(example_plot)

st.write('Es werden mehrere Plots auf der finalen Website sein, für Demonstrationszwecke reicht aber ein einzelner aus.')