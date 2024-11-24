import itertools
import json
import random
import uuid

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


def restart() -> None:
    adj_matrix = st.session_state.adj_matrix
    stim_a, stim_b = st.session_state.stimuli
    rel = round(st.session_state.relatedness / 100, 2)

    adj_matrix.at[stim_a, stim_b] = rel
    adj_matrix.at[stim_b, stim_a] = rel

    conn.create(
        worksheet=f'{st.session_state.user_name}_{st.session_state.user_id}',
        data=st.session_state.adj_matrix.reset_index()
    )

    st.session_state.relatedness_slider = 50
    st.session_state.current_index = 0


def start() -> None:
    if not st.session_state.name.strip():
        return

    st.session_state.user_name = st.session_state.name
    st.session_state.user_id = str(uuid.uuid4()).split('-')[0]
    st.session_state.relatedness_slider = 50
    st.session_state.current_index += 1


def next_question():
    adj_matrix = st.session_state.adj_matrix
    stim_a, stim_b = st.session_state.stimuli
    rel = round(st.session_state.relatedness / 100, 2)

    adj_matrix.at[stim_a, stim_b] = rel
    adj_matrix.at[stim_b, stim_a] = rel

    st.session_state.relatedness_slider = 50
    st.session_state.current_index += 1


def initial_view() -> None:
    st.title('Semantic Judgement Task')

    st.markdown(
        'In this task, please evaluate the semantic relatedness of pairs of words '
        'you will see on the screen. For example:'
    )
    st.html(
        """
        <div class="stimuli">
            <div class="stim-col">cat</div>
            <div class="stim-col">lamp</div>
        </div>    
        """
    )

    st.slider(
        label='How much are these words related?',
        min_value=0,
        max_value=100,
        value=50,
        format='',
        label_visibility='hidden'
    )

    with st.form('name'):
        st.text_input('Your name:', max_chars=20, key='name')
        st.form_submit_button('Start', on_click=start)


def question_view() -> None:
    pairs = st.session_state.pairs

    st.progress(st.session_state.current_index / len(pairs))

    stim_a, stim_b = pairs[st.session_state.current_index - 1]
    st.html(
        f"""
        <div class="stimuli">
            <div class="stim-col">{stim_a}</div>
            <div class="stim-col">{stim_b}</div>
        </div>    
        """
    )

    rel = st.slider(
        label='How much are these words related?',
        min_value=0,
        max_value=100,
        format='',
        label_visibility='hidden',
        key='relatedness_slider'
    )
    st.session_state.relatedness = rel
    st.session_state.stimuli = (stim_a, stim_b)

    if st.session_state.current_index < len(pairs):
        st.button('Submit', on_click=next_question)
    else:
        st.button('Submit', on_click=restart)


st.set_page_config(
    page_title='Semantic judgement task'
)

st.html(
    """
    <style>
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    }
    
    div[data-testid="stSliderTickBarMin"]::before {
        content: "unrelated"
    }
    
    div[data-testid="stSliderTickBarMax"]::before {
        content: "strongly related";
    }
    
    .stimuli {
        display: flex; 
        flex-direction: row;
        flex-wrap: wrap;
        width: 100%;
        margin-top: 6em;
        margin-bottom: 6em;
    }
    
    .stim-col {
        display: flex;
        flex-direction: column;
        flex-basis: 100%;
        flex: 1;
        font-size: 2.25rem;
        font-weight: 600;
        line-height: 1.2;
        text-align: center;
    }
    
    div:has(> div[role="slider"]) {
        background: rgba(172, 177, 195, 0.25);
    }
    </style>
    """
)

st.session_state.setdefault('current_index', 0)
st.session_state.setdefault('relatedness', 50)

if 'pairs' not in st.session_state:
    with open('data/stimuli.json', 'r', encoding='utf-8') as f:
        words = sum(json.load(f).values(), [])

    pairs = [
        random.sample(pair, 2)
        for pair in itertools.combinations(words, 2)
    ]
    random.shuffle(pairs)

    st.session_state['pairs'] = pairs
    st.session_state['adj_matrix'] = pd.DataFrame(
        data=0.0,
        index=pd.Index(words),
        columns=pd.Index(words)
    )
else:
    pairs = st.session_state['pairs']
    adj_matrix = st.session_state['adj_matrix']

conn = st.connection('gsheets', type=GSheetsConnection)

if st.session_state.current_index == 0:
    initial_view()
else:
    question_view()
