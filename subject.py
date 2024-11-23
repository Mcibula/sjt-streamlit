import itertools
import json
import random

import streamlit as st


def restart() -> None:
    st.session_state.current_index = 0


def start() -> None:
    if st.session_state.name.strip():
        st.session_state.relatedness_slider = 50
        st.session_state.current_index += 1


def next_question():
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

    if st.session_state.current_index < len(pairs):
        st.button('Submit', on_click=next_question)
    else:
        st.button('Restart', on_click=restart)


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
else:
    pairs = st.session_state['pairs']

if st.session_state.current_index == 0:
    initial_view()
else:
    question_view()
