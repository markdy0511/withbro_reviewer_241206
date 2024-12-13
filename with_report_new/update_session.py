import streamlit as st

def update_selected_items(session_key, selected):
    #Multiselect 값이 변경될 때 세션 상태를 즉시 업데이트
    st.session_state[session_key] = selected

def update_selected_items_dic(session_key_mom,session_key_child, selected):
    #Multiselect 값이 변경될 때 세션 상태를 즉시 업데이트
    st.session_state[session_key_mom][session_key_child] = selected