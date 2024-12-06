#보고서 유형 저장
import streamlit as st
from datetime import datetime

def init_session_state():
    if 'condition_set' not in st.session_state:
        st.session_state.condition_set = {'commerce_or_not': '커머스', 'analysis_period': '일간', 'selected_date':datetime.today().date(), 'week_start_day':'월요일'}

    #df 저장
    if 'df_set' not in st.session_state:
        st.session_state.df_set = None

    #기간 저장
    if 'period_set' not in st.session_state:
        st.session_state.period_set = None

    #지표 유형별 리스트 저장
    if 'metric_set' not in st.session_state:
        st.session_state.metric_set = None

    #전환 지표 유형별 리스트 저장
    if 'trans_metric_set' not in st.session_state:
        st.session_state.trans_metric_set = {'selected_trans_media': None, 'selected_trans_ga': None}

    #전환 지표 유형별 리스트 저장
    if 'cal_trans_metric_set' not in st.session_state:
        st.session_state.cal_trans_metric_set = {'selected_trans_media': None, 'selected_trans_ga': None}

    #오버뷰 결과물
    if 'overview_result' not in st.session_state:
        st.session_state.overview_result = None

    #매체별 결과물
    if 'ch_ranking_result' not in st.session_state:
        st.session_state.ch_ranking_result = None

    #소재별 결과물
    if 'brnch_ranking_result' not in st.session_state:
        st.session_state.brnch_ranking_result = None

    #소재구분별 결과물
    if 'brnch_detail_result' not in st.session_state:
        st.session_state.brnch_detail_result = None

    #캠페인별 결과물
    if 'cmp_ranking_result' not in st.session_state:
        st.session_state.cmp_ranking_result = {"channel":None, "selected_metrics":None}

    #광고그룹별 결과물
    if 'grp_ranking_result' not in st.session_state:
        st.session_state.grp_ranking_result = {"campaign":None}

    #소재명/키워드별 결과물
    if 'kwrd_ranking_result' not in st.session_state:
        st.session_state.kwrd_ranking_result = {}

    #캠페인별 결과물
    if 'da_cmp_ranking_result' not in st.session_state:
        st.session_state.da_cmp_ranking_result = {}

    #광고그룹별 결과물
    if 'da_grp_ranking_result' not in st.session_state:
        st.session_state.da_grp_ranking_result = {}

    #소재명/키워드별 결과물
    if 'da_kwrd_ranking_result' not in st.session_state:
        st.session_state.da_kwrd_ranking_result = {}

    #운영히스토리
    if 'history_result' not in st.session_state:
        st.session_state.history_result = {}

    #운영히스토리
    if 'commerce_or_not' not in st.session_state:
        st.session_state.commerce_or_not = '커머스'

    if "raw" not in st.session_state:
        st.session_state.raw = {"media_file": None,"media_columns": None,"ga_file": None,"ga_columns": None ,"history_file": None,"history_columns": None}

    if "start" not in st.session_state:
        st.session_state.start = None

    if "type_ad_owner" not in st.session_state:
        st.session_state["type_ad_owner"] = "커머스"

    if "previous_version" not in st.session_state:
        st.session_state["previous_version"] = -1
    
    if "current_version" not in st.session_state:
        st.session_state["current_version"] = 0
    
    if "brnch_dsply" not in st.session_state:
        st.session_state["brnch_dsply"] = 1

    if "cmp_previous_version" not in st.session_state:
        st.session_state["cmp_previous_version"] = -1
    
    if "cmp_current_version" not in st.session_state:
        st.session_state["cmp_current_version"] = 0

    if "da_cmp_previous_version" not in st.session_state:
        st.session_state["da_cmp_previous_version"] = -1
    
    if "da_cmp_current_version" not in st.session_state:
        st.session_state["da_cmp_current_version"] = 0

    if "br_previous_version" not in st.session_state:
        st.session_state["br_previous_version"] = -1
    
    if "br_current_version" not in st.session_state:
        st.session_state["br_current_version"] = 0

    return None