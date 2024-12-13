import streamlit as st
from datetime import datetime
import pandas as pd


st.set_page_config(
    page_title="Report Assistant_test",
    page_icon="🐥",
    layout="wide",
)

import insert_logo 
from with_report_new import condition_select, overview_writer, preprocessing_init_data, choose_trans_metric, export_info, bullet_output, ch_ranking_writer, detail_writer, keyword_writer, history_writer, update_session, init_session_state, graph
from with_report_new import overview_writer_new
from with_report_new.load_data import load
from with_report_new.export_info import get_week_info, get_month_info
from with_report_new.formatting_init_data import format_media, format_ga, format_history
from with_report_new.period_filter import filter_by_period
from with_report_new.arrange_metric import arrange_metric


insert_logo.add_logo("withbrother_logo.png")

init_session_state.init_session_state()


org_sort_orders = {
    '노출수': False,  # 내림차순
    '클릭수': False,  # 내림차순
    'CTR': False,  # 내림차순'
    'CPC': True,  # 오름차순
    '총비용': False,  # 내림차순
    '전환수': False,  # 내림차순
    'CPA': True,  # 오름차순
    'GA_전환수': False,  # 내림차순
    'GA_CPA': True,  # 오름차순
}

# Streamlit app layout
st.title('보고서 작성 도우미')



# 데이터 입력기
with st.sidebar: #원하는 소스를 만드는 곳
    st.sidebar.header('이곳에 데이터를 업로드하세요.')

    commerce_or_not = st.selectbox(
        "광고주가 커머스 분야인가요? 아니면 비커머스 분야인가요? (필수)",
        ("커머스", "비커머스"),
        key="type_ad_owner",  # 상태 키 설정
        on_change=lambda: update_session.update_selected_items_dic('condition_set','commerce_or_not',st.session_state["type_ad_owner"]),
    )
    media_file = st.file_uploader(
        "매체 데이터 업로드 (Excel or CSV)",
        type=['xls','xlsx', 'csv'],
        key="uploader1"
    )
    ga_file = st.file_uploader(
        "GA 데이터 업로드 (Excel or CSV)",
        type=['xls','xlsx', 'csv'],
        key="uploader2"
    )

    history_file = st.file_uploader(
        "운영 히스토리 데이터 업로드 (Excel or CSV)",
        type=["xls", "xlsx", "csv"],
        key="uploader3"
    )

    upload_button = st.button("데이터 업로드")

if media_file and ga_file and history_file and upload_button:
    # 파일이 변경되었는지 확인
    st.session_state.start = 1
    if media_file and media_file != st.session_state.raw["media_file"]:
        st.session_state.raw["media_file"] = media_file
        # 새 파일 읽기 및 열 정보 업데이트
        original_media_df = load(media_file)
        st.session_state.raw["media_columns"] = list(set(original_media_df.columns.tolist()) - set(['일자','캠페인','광고그룹','소재명/키워드','디바이스','노출수','클릭수','총비용','매체','소재구분','소재종류','광고유형']))

    if ga_file and ga_file != st.session_state.raw["ga_file"]:
        st.session_state.raw["ga_file"] = ga_file
        # 새 파일 읽기 및 열 정보 업데이트
        original_ga_df = load(ga_file)
        st.session_state.raw["ga_columns"] = list(set(original_ga_df.columns.tolist()) - set(['일자','캠페인','광고그룹','소재명/키워드','디바이스','매체','소재구분','소재종류','광고유형']))

    if history_file and history_file != st.session_state.raw["history_file"]:
        st.session_state.raw["history_file"] = history_file
        # 새 파일 읽기 및 열 정보 업데이트
        original_history_df = load(history_file)
        st.session_state.raw["history_columns"] = original_history_df.columns.tolist()
elif st.session_state.start and ((media_file is None) or (ga_file is None) or (history_file is None)):
    st.session_state.clear()
    st.cache_data.clear()
    init_session_state.init_session_state()
    
else:
    init_session_state.init_session_state()
    pass

st.subheader('보고서 조건 선택')
analysis_period = st.radio(
    "분석할 기간을 선택하세요 (필수)",
    ("일간", "주간", "월간"),
    key="analysis_period",  # 상태 키 설정
    on_change=lambda: update_session.update_selected_items_dic('condition_set','analysis_period',st.session_state["analysis_period"]),
)
selected_date = st.date_input(
    "분석 시작 날짜를 선택해주세요. 주간, 월간일 경우 포함 날짜 아무 일이나 선택해주세요. (필수)",
    value=st.session_state.condition_set['selected_date'],
    key="selected_date",
    on_change=lambda: update_session.update_selected_items_dic('condition_set','selected_date',st.session_state["selected_date"]),
)

week_start_day = st.radio(
    "주의 시작 요일을 선택하세요. 주간 분석을 하지 않을 경우 아무것이나 선택해도 됩니다. (선택)",
        ("월요일", "일요일"),
        key="selected_starting",
        on_change=lambda: update_session.update_selected_items_dic('condition_set','week_start_day',st.session_state["selected_starting"]),
    )


try:
    filtered_trans_list = [item for item in st.session_state.raw["media_columns"] if "구매액" not in item]
    filtered_ga_trans_list = [item for item in st.session_state.raw["ga_columns"] if "구매액" not in item]
except:
    filtered_trans_list = None
    filtered_ga_trans_list = None

selected_trans_media = st.multiselect(
    "매체 데이터에서 표에 출력할 전환 지표들을 선택해주세요.",
    filtered_trans_list,
    default=st.session_state.trans_metric_set['selected_trans_media'],  # 기존 선택 상태 유지
    key="temp_trans_media",  # 상태 키 설정
    on_change=lambda: update_session.update_selected_items_dic('trans_metric_set','selected_trans_media',st.session_state["temp_trans_media"]),
)
selected_trans_ga = st.multiselect(
    "GA 데이터에서 표에 출력할 전환 지표들을 선택해주세요.",
    filtered_ga_trans_list,
    default=st.session_state.trans_metric_set['selected_trans_ga'],  # 기존 선택 상태 유지
    key="temp_trans_ga",  # 상태 키 설정
    on_change=lambda: update_session.update_selected_items_dic('trans_metric_set','selected_trans_ga',st.session_state["temp_trans_ga"]),
)

num_day = st.radio("추세 분석 기간을 선택해주세요. (선택)",
        ("7일", "14일", "28일"),
        key="selected_num_day",
    )

report_gen = st.button("보고서 생성")

if report_gen:
    st.session_state["current_version"] += 1
    if st.session_state["previous_version"] < 0:
        st.session_state["previous_version"] = 0

if (st.session_state["previous_version"] >= 0):

    with st.spinner("보고서 초안 생성 중..."):
        grouping_period = export_info.get_group_kwr(st.session_state.condition_set["analysis_period"])
        st.session_state.df_set, st.session_state.period_set, st.session_state.metric_set, st.session_state.cal_trans_metric_set = preprocessing_init_data.filtering_data(media_file, ga_file, history_file, st.session_state.condition_set)
    
    data_col, history_col = st.columns([3,2])
    with data_col:
        overview, sa_perform, da_perform  = st.tabs(["오버뷰","SA 성과","DA 성과"])
        with overview:

            if (st.session_state["previous_version"] != st.session_state["current_version"]): #보고서 업데이트
                #오버뷰 생성
                with st.spinner('전체 데이터 분석 중...'):
                    rounded_overview_df, filtered_overview_df, all_col_list = overview_writer_new.overview_df(
                        st.session_state.df_set['used_media'],
                        st.session_state.df_set['used_ga'],
                        st.session_state.metric_set,
                        st.session_state.cal_trans_metric_set,
                        st.session_state.trans_metric_set,
                        grouping_period,
                        st.session_state.condition_set,
                        st.session_state.period_set)
                    overview_statement, overview_statement_summary = overview_writer_new.writer(rounded_overview_df, all_col_list)
            
                st.session_state.overview_result = {'overview_df':rounded_overview_df,'filtered_df':filtered_overview_df,'overview_statement':overview_statement,'overview_statement_summary':overview_statement_summary}
                
                #매체별 생성
                ch_ranking_df, filtered_ch_ranking_df, ch_all_col_list = ch_ranking_writer.ch_ranking_df(
                    st.session_state.df_set['used_media'],
                    st.session_state.df_set['used_ga'],
                    '매체',
                    st.session_state.metric_set,
                    st.session_state.cal_trans_metric_set,
                    st.session_state.trans_metric_set,
                    grouping_period,
                    st.session_state.condition_set,
                )
                

                now_period_result, sort_order = ch_ranking_writer.display_period_data(
                    st.session_state.period_set["now"],
                    ch_ranking_df,
                    st.session_state.overview_result['overview_df'],
                    '매체',
                    grouping_period,
                    None
                )


                st.session_state.ch_ranking_result = {"now_result_df":now_period_result}

                pre_period_result, _ = ch_ranking_writer.display_period_data(
                    st.session_state.period_set["pre"],
                    ch_ranking_df,
                    st.session_state.overview_result['overview_df'],
                    '매체',
                    grouping_period,
                    sort_order
                )
                

                st.session_state.ch_ranking_result["pre_result_df"] = pre_period_result

                st.session_state.ch_ranking_result["sort_order"] = sort_order
                channels = [x for x in now_period_result['매체'].unique() if x != '합계']

                ch_overview_df_dic = {}
                ch_overview_st_dic = {}
                ch_overview_st_dic_summary = {}
                with st.spinner('매체별 데이터 분석 중...'):
                    for channel in channels:
                        if str(channel) == '정보없음':
                            continue
                        rounded_overview_ch_df, rounded_overview_ch_df_filtered = ch_ranking_writer.ch_df(
                            ch_ranking_df, '매체', channel, st.session_state.metric_set, st.session_state.trans_metric_set,
                            grouping_period, 
                            st.session_state.period_set,
                            st.session_state.condition_set,
                        )
                        overview_ch_statement, overview_ch_statement_summary = overview_writer_new.writer(rounded_overview_ch_df, all_col_list)
                        
                        ch_overview_df_dic[channel] = rounded_overview_ch_df_filtered
                        ch_overview_st_dic[channel] = overview_ch_statement
                        ch_overview_st_dic_summary[channel] = overview_ch_statement_summary

                st.session_state.ch_ranking_result["ch_overview_df_dic"] = ch_overview_df_dic
                st.session_state.ch_ranking_result["ch_overview_st_dic"] = ch_overview_st_dic
                st.session_state.ch_ranking_result["ch_overview_st_dic_summary"] = ch_overview_st_dic_summary


                if st.session_state.df_set['used_media']['소재구분'].isnull().all():
                    st.session_state["brnch_dsply"]= 0
                    #st.write('매체 데이터에서 소재구분 데이터가 없는 기간입니다.')
                else:
                    
                    filtered_media_df = st.session_state.df_set['used_media'].dropna(subset=['소재구분'])
                    filtered_ga_df = st.session_state.df_set['used_ga'].dropna(subset=['소재구분'])
                    
                    brnch_ranking_df, filtered_brnch_ranking_df, br_all_col_list = ch_ranking_writer.ch_ranking_df(
                        filtered_media_df,
                        filtered_ga_df,
                        '소재구분',
                        st.session_state.metric_set,
                        st.session_state.cal_trans_metric_set,
                        st.session_state.trans_metric_set,
                        grouping_period,
                        st.session_state.condition_set,
                    )

                    now_period_result, sort_order = ch_ranking_writer.display_period_data(
                            st.session_state.period_set["now"],
                            brnch_ranking_df,
                            st.session_state.overview_result['overview_df'],
                            '소재구분',
                            grouping_period,
                            None
                        )

                    st.session_state.brnch_ranking_result = {"now_result_df":now_period_result}
                    

                    pre_period_result, _ = ch_ranking_writer.display_period_data(
                            st.session_state.period_set["pre"],
                            brnch_ranking_df,
                            st.session_state.overview_result['overview_df'],
                            '소재구분',
                            grouping_period,
                            sort_order
                        )

                    st.session_state.brnch_ranking_result["pre_result_df"] = pre_period_result

                    st.session_state.brnch_ranking_result["sort_order"] = sort_order
                    brnchs = [x for x in now_period_result['소재구분'].unique() if x != '합계']

                    brnch_overview_df_dic = {}
                    brnch_overview_st_dic = {}
                    brnch_overview_st_dic_summary = {}
                    with st.spinner('소재별 데이터 분석 중...'):
                        for brnch in brnchs:
                            if str(brnch) == '정보없음':
                                continue
                            rounded_overview_brnch_df, rounded_overview_brnch_df_filtered = ch_ranking_writer.ch_df(
                                brnch_ranking_df, '소재구분', brnch, st.session_state.metric_set, st.session_state.trans_metric_set,
                                grouping_period,
                                st.session_state.period_set,
                                st.session_state.condition_set,
                            )
                            overview_brnch_statement, overview_brnch_statement_summary = overview_writer_new.writer(rounded_overview_brnch_df, all_col_list)
                            
                            brnch_overview_df_dic[brnch] = rounded_overview_brnch_df_filtered
                            brnch_overview_st_dic[brnch] = overview_brnch_statement
                            brnch_overview_st_dic_summary[brnch] = overview_brnch_statement_summary


                    st.session_state.brnch_ranking_result["brnch_overview_df_dic"] = brnch_overview_df_dic
                    st.session_state.brnch_ranking_result["brnch_overview_st_dic"] = brnch_overview_st_dic
                    st.session_state.brnch_ranking_result["brnch_overview_st_dic_summary"] = brnch_overview_st_dic_summary

            else:
                pass
            
            #오버뷰 출력
            st.subheader('오버뷰')
            graph.trend_days(st.session_state.condition_set['selected_date'], st.session_state.df_set, st.session_state.condition_set['commerce_or_not'], int(num_day[:-1]))
            st.write(st.session_state.overview_result['filtered_df'])
            with st.expander("전체 지표 별 변화 문구"):
                bullet_output.print_dic_bullet(st.session_state.overview_result['overview_statement'])
            summary_text_1 = st.session_state.overview_result['overview_statement_summary']['총평'].split('. ')
            st.write(f"**총평**:")
            for s in summary_text_1:
                st.write("- ", s)
            #bullet_output.print_dic_bullet(st.session_state.overview_result['overview_statement_summary'])

            st.session_state["previous_version"] = st.session_state["current_version"]

        with sa_perform:    
            selected_ad_type = "SA"
            st.session_state.SA_result = {"ad_type":selected_ad_type}

            filtered_type_df = st.session_state.df_set['used_media'][st.session_state.df_set['used_media']["광고유형"] == selected_ad_type]
            filtered_ga_type_df = st.session_state.df_set['used_ga'][st.session_state.df_set['used_ga']["광고유형"] == selected_ad_type]

            st.write("분석하고자 하는 매체를 선택해주세요.")
            selected_channel = st.selectbox(
                "매체 선택",
                filtered_type_df["매체"].dropna().unique()
            )
            
            st.session_state.SA_result["channel"] = selected_channel
            st.session_state.cmp_ranking_result["channel"] = selected_channel

            overview_sa, cmp_sa, grp_sa, kwrd_sa  = st.tabs(["전체 성과 분석","캠페인 분석","그룹 분석", "성과 상위 키워드 분석"])
            with overview_sa:
                st.subheader(selected_channel)
                st.write(st.session_state.ch_ranking_result["ch_overview_df_dic"][selected_channel])
                with st.expander("전체 지표 별 변화 문구"):
                    bullet_output.print_dic_bullet(st.session_state.ch_ranking_result["ch_overview_st_dic"][selected_channel])
                summary_text_2 = st.session_state.ch_ranking_result['ch_overview_st_dic_summary'][selected_channel]['총평'].split('. ')
                st.write(f"**총평**:")
                for s in summary_text_2:
                    st.write("- ", s)
                #bullet_output.print_dic_bullet(st.session_state.ch_ranking_result["ch_overview_st_dic_summary"][selected_channel])

            with cmp_sa:
                sort_orders_cmp = org_sort_orders
                metrics = st.session_state.overview_result['overview_df'].columns.tolist()

                for metric in metrics:
                    if metric not in org_sort_orders.keys():
                        sort_orders_cmp[metric] = False
                    else:
                        pass
                
                submit_button_cmp, sort_columns_cmp = detail_writer.choose_metric(metrics,2)

                st.session_state.cmp_ranking_result["submit_button"] = submit_button_cmp
                st.session_state.cmp_ranking_result["metric_sort_order"] = sort_orders_cmp
                st.session_state.cmp_ranking_result["selected_metrics"] = sort_columns_cmp

                filtered_cmp_df = filtered_type_df[filtered_type_df["매체"] == selected_channel]
                filtered_ga_cmp_df = filtered_ga_type_df[filtered_ga_type_df["매체"] == selected_channel]

                st.session_state.cmp_ranking_result["cmp_df"] = filtered_cmp_df
                st.session_state.cmp_ranking_result["ga_cmp_df"] = filtered_ga_cmp_df

                if submit_button_cmp:
                    st.session_state["cmp_current_version"] += 1
                    if st.session_state["cmp_previous_version"] < 0:
                        st.session_state["cmp_previous_version"] = 0

                if (st.session_state["cmp_previous_version"] >= 0):
                    if (st.session_state["cmp_previous_version"] != st.session_state["cmp_current_version"]):
                        detail_cmp_df, metric_filtered_detail_cmp_df, dtl_cmp_all_col_list  = ch_ranking_writer.ch_ranking_df(
                            filtered_cmp_df,
                            filtered_ga_cmp_df,
                            '캠페인',
                            st.session_state.metric_set,
                            st.session_state.cal_trans_metric_set,
                            st.session_state.trans_metric_set,
                            grouping_period,
                            st.session_state.condition_set,
                        )
                        
                        filtered_detail_cmp_df = metric_filtered_detail_cmp_df[metric_filtered_detail_cmp_df[grouping_period] == st.session_state.period_set["now"]]

                        sorted_cmp_df, top_cmp_num, cmp_statements = detail_writer.display_top(
                            sort_columns_cmp,
                            sort_orders_cmp,
                            filtered_detail_cmp_df, 
                            st.session_state.overview_result['overview_df'],
                        )

                        st.session_state.cmp_ranking_result['top_cmp_detail_df'] = sorted_cmp_df
                        st.session_state.cmp_ranking_result['top_num_cmp_detail'] = top_cmp_num
                        st.session_state.cmp_ranking_result['cmp_detail_statment'] = cmp_statements

                        st.write('정렬된 상위 ' + str(top_cmp_num) + '개 캠페인')
                        st.write(sorted_cmp_df)

                        #for statement in cmp_statements:
                        #    st.write(statement)

                        try:
                            description_cmp_detail = detail_writer.writer(top_cmp_num, sorted_cmp_df, sort_columns_cmp, "캠페인")

                            st.session_state.cmp_ranking_result['description_cmp_detail'] = description_cmp_detail

                            #st.write(description_cmp_detail)
                            bullet_output.display_analysis(description_cmp_detail,sorted_cmp_df.columns.to_list(), "캠페인")
                        except:
                            st.session_state.cmp_ranking_result['description_cmp_detail'] = "1데이터 정합성을 확인해주세요."
                            st.write("2데이터 정합성을 확인해주세요.")
                    else:
                        st.write('정렬 기준 지표를 선택한 후, 정렬 적용 버튼을 눌러주세요.')
                        if 'description_cmp_detail' in st.session_state.cmp_ranking_result.keys():
                            st.write('정렬된 상위 ' + str(st.session_state.cmp_ranking_result['top_num_cmp_detail']) + '개 매체')
                            st.write(st.session_state.cmp_ranking_result['top_cmp_detail_df'])

                            #for statement in st.session_state.cmp_ranking_result['cmp_detail_statment']:
                            #    st.write(statement)
                            st.write(st.session_state.cmp_ranking_result['description_cmp_detail'])
                            #ullet_output.display_analysis(st.session_state.cmp_ranking_result['description_cmp_detail'],st.session_state.cmp_ranking_result['top_cmp_detail_df'].columns.to_list(), "캠페인")
                            try:
                                bullet_output.display_analysis(st.session_state.cmp_ranking_result['description_cmp_detail'],st.session_state.cmp_ranking_result['top_cmp_detail_df'].columns.to_list(), "캠페인")
                            except:
                                st.write("3데이터 정합성을 확인해주세요.")
                else:
                    pass
            with grp_sa:
                st.header("그룹 분석")
                st.write("분석하고자 하는 캠페인을 선택해주세요.")
                if 'description_cmp_detail' in st.session_state.cmp_ranking_result.keys():
                    st.write("아래는 " + st.session_state.cmp_ranking_result["channel"] + "의 캠페인 목록입니다.")
                    
                    selected_campaign = st.selectbox(
                        "캠페인 선택",
                        st.session_state.cmp_ranking_result["cmp_df"]["캠페인"].dropna().unique(),
                    )

                    st.session_state.grp_ranking_result = {"campaign" : selected_campaign}

                    filtered_grp_df = st.session_state.df_set["used_media"][(st.session_state.df_set["used_media"]["매체"] == st.session_state.cmp_ranking_result["channel"]) & (st.session_state.df_set["used_media"]["캠페인"] == selected_campaign)]
                    filtered_ga_grp_df = st.session_state.df_set["used_ga"][(st.session_state.df_set["used_ga"]["매체"] == st.session_state.cmp_ranking_result["channel"]) & (st.session_state.df_set["used_ga"]["캠페인"] == selected_campaign)]

                    st.session_state.grp_ranking_result["grp_df"] = filtered_grp_df
                    st.session_state.grp_ranking_result["ga_grp_df"] = filtered_ga_grp_df

                    detail_grp_df, metric_filtered_detail_grp_df, dtl_grp_all_col_list = ch_ranking_writer.ch_ranking_df(
                        filtered_grp_df,
                        filtered_ga_grp_df,
                        '광고그룹',
                        st.session_state.metric_set,
                        st.session_state.cal_trans_metric_set,
                        st.session_state.trans_metric_set,
                        grouping_period,
                        st.session_state.condition_set,
                    )

                    filtered_detail_grp_df = metric_filtered_detail_grp_df[metric_filtered_detail_grp_df[grouping_period] == st.session_state.period_set["now"]]

                    if len(filtered_detail_grp_df) == 0:
                        st.write("이번 기간에는 운영되지 않은 캠페인입니다.")
                    else:
                        sorted_grp_df, top_grp_num, grp_statements = detail_writer.display_top(
                            st.session_state.cmp_ranking_result["selected_metrics"],
                            st.session_state.cmp_ranking_result["metric_sort_order"],
                            filtered_detail_grp_df, 
                            st.session_state.overview_result['overview_df'],
                        )

                        st.session_state.grp_ranking_result['top_grp_detail_df'] = sorted_grp_df
                        st.session_state.grp_ranking_result['top_num_grp_detail'] = top_grp_num
                        st.session_state.grp_ranking_result['grp_detail_statment'] = grp_statements

                        st.write('정렬된 상위 ' + str(top_grp_num) + '개 광고그룹')
                        st.write(sorted_grp_df)

                        #for statement in grp_statements:
                        #    st.write(statement)

                        try:
                            description_grp_detail = detail_writer.writer(top_grp_num, sorted_grp_df, st.session_state.cmp_ranking_result["selected_metrics"], "광고그룹")

                            st.session_state.grp_ranking_result['description_grp_detail'] = description_grp_detail

                            #st.write(description_grp_detail)
                            bullet_output.display_analysis(description_grp_detail, sorted_grp_df.columns.to_list(), "광고그룹")
                        except:
                            st.write("데이터 정합성을 확인해주세요.")
                else:
                    st.write("캠페인 분석 탭을 먼저 실행해주세요.")
            with kwrd_sa:
                st.header("키워드별 성과 분석")
                st.write("성과 상위 키워드를 분석합니다.")
                st.write("※ 아래는 이전 선택들과 별개입니다.")
                
                #매체 선택 필터
                can_channel_list = ["선택안함"] + list(filtered_type_df["매체"].dropna().unique())
                kwrd_selected_channel = st.selectbox(
                        "- **매체 선택**",
                        can_channel_list,
                        index=can_channel_list.index(st.session_state.SA_result["channel"])
                    )
                
                #캠페인 선택 필터
                if kwrd_selected_channel != "선택안함":
                    kwrd_filtered_cmp_df = filtered_type_df[filtered_type_df["매체"] == kwrd_selected_channel]
                    kwrd_selected_cmp = st.selectbox(
                            "- **캠페인 선택**",
                            ["선택안함"] + list(kwrd_filtered_cmp_df["캠페인"].dropna().unique()),
                            index=0
                        )
                else:
                    kwrd_selected_cmp = st.selectbox(
                            "- **캠페인 선택**",
                            ["선택안함"] + list(filtered_type_df["캠페인"].dropna().unique()),
                            index=0
                        )

                #광고그룹 선택 필터
                if (kwrd_selected_channel != "선택안함") or (kwrd_selected_cmp != "선택안함"):
                    if (kwrd_selected_channel != "선택안함") and (kwrd_selected_cmp != "선택안함"):
                        kwrd_filtered_grp_df = filtered_type_df[(filtered_type_df["매체"] == kwrd_selected_channel) & (filtered_type_df["캠페인"] == kwrd_selected_cmp)]
                    else:
                        if (kwrd_selected_channel != "선택안함"):
                            kwrd_filtered_grp_df = filtered_type_df[filtered_type_df["매체"] == kwrd_selected_channel]
                        else:
                            kwrd_filtered_grp_df = filtered_type_df[filtered_type_df["캠페인"] == kwrd_selected_cmp]
                    
                    kwrd_selected_grp = st.selectbox(
                                "- **광고그룹 선택**",
                                ["선택안함"] + list(kwrd_filtered_grp_df["광고그룹"].dropna().unique()),
                                index=0
                            )
                else:
                    kwrd_selected_grp = st.selectbox(
                            "- **광고그룹 선택**",
                            ["선택안함"] + list(filtered_type_df["광고그룹"].dropna().unique()),
                            index=0
                        )
                
                media_df_cleaned = st.session_state.df_set["used_media"].dropna(subset=['소재명/키워드'])
                ga_df_cleaned = st.session_state.df_set["used_ga"].dropna(subset=['소재명/키워드'])

                #데이터 필터링
                if (kwrd_selected_channel != "선택안함") or (kwrd_selected_cmp != "선택안함") or (kwrd_selected_grp != "선택안함"):
                    # 필터링 조건 초기화
                    conditions_media = [True] * len(media_df_cleaned)
                    conditions_ga = [True] * len(ga_df_cleaned)

                    # 조건에 따라 필터링
                    if kwrd_selected_channel != "선택안함":
                        conditions_media &= media_df_cleaned['매체'] == kwrd_selected_channel
                        conditions_ga &= ga_df_cleaned['매체'] == kwrd_selected_channel

                    if kwrd_selected_cmp != "선택안함":
                        conditions_media &= media_df_cleaned['캠페인'] == kwrd_selected_cmp
                        conditions_ga &= ga_df_cleaned['캠페인'] == kwrd_selected_cmp

                    if kwrd_selected_grp != "선택안함":
                        conditions_media &= media_df_cleaned['광고그룹'] == kwrd_selected_grp
                        conditions_ga &= ga_df_cleaned['광고그룹'] == kwrd_selected_grp

                    # 필터링 적용
                    filtered_media_df_cleaned = media_df_cleaned[conditions_media]
                    filtered_ga_df_cleaned = ga_df_cleaned[conditions_ga]
                else:
                    filtered_media_df_cleaned = media_df_cleaned
                    filtered_ga_df_cleaned = ga_df_cleaned

                try:
                    detail_kwrd_df, metric_filtered_detail_kwrd_df, dtl_kwrd_all_col_list = keyword_writer.detail_kwrd_ranking_df(
                                filtered_media_df_cleaned,
                                filtered_ga_df_cleaned,
                                '소재명/키워드',
                                st.session_state.metric_set,
                                st.session_state.cal_trans_metric_set,
                                st.session_state.trans_metric_set,
                                grouping_period,
                                st.session_state.condition_set,
                            )
                    filtered_detail_kwrd_df = metric_filtered_detail_kwrd_df[metric_filtered_detail_kwrd_df[grouping_period] == st.session_state.period_set["now"]]

                    if not filtered_detail_kwrd_df.empty:
                        kwrd_ascending_orders = [st.session_state.cmp_ranking_result["metric_sort_order"][col] for col in st.session_state.cmp_ranking_result["selected_metrics"]]
                        sorted_detail_kwrd_df = filtered_detail_kwrd_df.sort_values(by="총비용", ascending=False)
                        st.write(sorted_detail_kwrd_df)
                        
                        kwrd_statements = keyword_writer.writer_new(
                            filtered_detail_kwrd_df,
                            st.session_state.cmp_ranking_result["selected_metrics"],
                            st.session_state.cmp_ranking_result["metric_sort_order"],
                        )
                    else:
                        st.write("이번 기간에는 운영된 소재/키워드가 없습니다.")

                except:
                    st.write("**※※ 매체데이터와 GA 데이터 결합에 문제가 있어, '소재명/키워드'로 필터링된 각각의 데이터를 출력합니다. ※※**")
                    st.write(filtered_media_df_cleaned, filtered_ga_df_cleaned)
                # if len(filtered_detail_kwrd_df) == 0:
                #     st.write("이번 기간에는 운영된 소재/키워드가 없습니다.")
                # else:
                #     pass
                #     keyword_ranking_df = keyword_writer.kwrd_ranking_df(
                #         filtered_media_df_cleaned,
                #         filtered_ga_df_cleaned,
                #         st.session_state.metric_set,
                #         st.session_state.cal_trans_metric_set,
                #         grouping_period,
                #         st.session_state.condition_set,
                #     )
                #     kwrd_statements = keyword_writer.writer_new(
                #         filtered_detail_kwrd_df,
                #         st.session_state.cmp_ranking_result["selected_metrics"],
                #         st.session_state.cmp_ranking_result["metric_sort_order"],
                #     )



        with da_perform:
            da_selected_ad_type = "DA"
            st.session_state.DA_result = {"ad_type":selected_ad_type}

            da_filtered_type_df = st.session_state.df_set['used_media'][st.session_state.df_set['used_media']["광고유형"] == da_selected_ad_type]
            da_filtered_ga_type_df = st.session_state.df_set['used_ga'][st.session_state.df_set['used_ga']["광고유형"] == da_selected_ad_type]

            st.write("분석하고자 하는 매체를 선택해주세요.")
            da_selected_channel = st.selectbox(
                "매체 선택",
                da_filtered_type_df["매체"].dropna().unique()
            )
            da_brnch_list = list(da_filtered_type_df["소재구분"][da_filtered_type_df["매체"] == da_selected_channel].dropna().unique())
            st.session_state.DA_result["channel"] = da_selected_channel
            st.session_state.da_cmp_ranking_result["channel"] = da_selected_channel
            overview_da, cmp_da, grp_da, brnch_da, brnch_dtl_da, kwrd_da  = st.tabs(["전체 성과 분석","캠페인 분석","그룹 분석", "소재구분 분석", "소재종류 분석", "성과 상위 소재 분석"])
            with overview_da:
                st.subheader(da_selected_channel)
                st.write(st.session_state.ch_ranking_result["ch_overview_df_dic"][da_selected_channel])
                with st.expander("전체 지표 별 변화 문구"):
                    bullet_output.print_dic_bullet(st.session_state.ch_ranking_result["ch_overview_st_dic"][da_selected_channel])
                summary_text_3 = st.session_state.ch_ranking_result['ch_overview_st_dic_summary'][da_selected_channel]['총평'].split('. ')
                st.write(f"**총평**:")
                for s in summary_text_3:
                    st.write("- ", s)
                #bullet_output.print_dic_bullet(st.session_state.ch_ranking_result["ch_overview_st_dic_summary"][selected_channel])
            with cmp_da:
                sort_orders_da_cmp = org_sort_orders
                metrics = st.session_state.overview_result['overview_df'].columns.tolist()

                for metric in metrics:
                    if metric not in org_sort_orders.keys():
                        sort_orders_da_cmp[metric] = False
                    else:
                        pass
                
                submit_button_da_cmp, sort_columns_da_cmp = detail_writer.choose_metric(metrics,3)

                st.session_state.da_cmp_ranking_result["submit_button"] = submit_button_da_cmp
                st.session_state.da_cmp_ranking_result["metric_sort_order"] = sort_orders_da_cmp
                st.session_state.da_cmp_ranking_result["selected_metrics"] = sort_columns_da_cmp

                da_filtered_cmp_df = da_filtered_type_df[da_filtered_type_df["매체"] == da_selected_channel]
                da_filtered_ga_cmp_df = da_filtered_ga_type_df[da_filtered_ga_type_df["매체"] == da_selected_channel]

                st.session_state.da_cmp_ranking_result["cmp_df"] = da_filtered_cmp_df
                st.session_state.da_cmp_ranking_result["ga_cmp_df"] = da_filtered_ga_cmp_df

                if submit_button_da_cmp:
                    st.session_state["da_cmp_current_version"] += 1
                    if st.session_state["da_cmp_previous_version"] < 0:
                        st.session_state["da_cmp_previous_version"] = 0

                if (st.session_state["da_cmp_previous_version"] >= 0):
                    if (st.session_state["da_cmp_previous_version"] != st.session_state["da_cmp_current_version"]):

                        da_detail_cmp_df, da_metric_filtered_detail_cmp_df, da_dtl_cmp_all_col_list = ch_ranking_writer.ch_ranking_df(
                            da_filtered_cmp_df,
                            da_filtered_ga_cmp_df,
                            '캠페인',
                            st.session_state.metric_set,
                            st.session_state.cal_trans_metric_set,
                            st.session_state.trans_metric_set,
                            grouping_period,
                            st.session_state.condition_set,
                        )
                        
                        da_filtered_detail_cmp_df = da_metric_filtered_detail_cmp_df[da_metric_filtered_detail_cmp_df[grouping_period] == st.session_state.period_set["now"]]

                        da_sorted_cmp_df, da_top_cmp_num, da_cmp_statements = detail_writer.display_top(
                            sort_columns_da_cmp,
                            sort_orders_da_cmp,
                            da_filtered_detail_cmp_df, 
                            st.session_state.overview_result['overview_df'],
                        )

                        st.session_state.da_cmp_ranking_result['top_cmp_detail_df'] = da_sorted_cmp_df
                        st.session_state.da_cmp_ranking_result['top_num_cmp_detail'] = da_top_cmp_num
                        st.session_state.da_cmp_ranking_result['cmp_detail_statment'] = da_cmp_statements

                        st.write('정렬된 상위 ' + str(da_top_cmp_num) + '개 캠페인')
                        st.write(da_sorted_cmp_df)

                        #for statement in cmp_statements:
                        #    st.write(statement)

                        try:
                            da_description_cmp_detail = detail_writer.writer(da_top_cmp_num, da_sorted_cmp_df, sort_columns_da_cmp, "캠페인")

                            st.session_state.da_cmp_ranking_result['description_cmp_detail'] = da_description_cmp_detail

                            #st.write(description_cmp_detail)
                            bullet_output.display_analysis(da_description_cmp_detail,da_sorted_cmp_df.columns.to_list(), "캠페인")
                        except:
                            st.session_state.da_cmp_ranking_result['description_cmp_detail'] = "1데이터 정합성을 확인해주세요."
                            st.write("2데이터 정합성을 확인해주세요.")
                    else:
                        st.write('정렬 기준 지표를 선택한 후, 정렬 적용 버튼을 눌러주세요.')
                        if 'description_cmp_detail' in st.session_state.da_cmp_ranking_result.keys():
                            st.write('정렬된 상위 ' + str(st.session_state.da_cmp_ranking_result['top_num_cmp_detail']) + '개 매체')
                            st.write(st.session_state.da_cmp_ranking_result['top_cmp_detail_df'])

                            #for statement in st.session_state.da_cmp_ranking_result['cmp_detail_statment']:
                            #    st.write(statement)
                            #st.write(st.session_state.cmp_ranking_result['description_cmp_detail'])
                            try:
                                bullet_output.display_analysis(st.session_state.da_cmp_ranking_result['description_cmp_detail'],st.session_state.da_cmp_ranking_result['top_cmp_detail_df'].columns.to_list(), "캠페인")
                            except:
                                st.write("3데이터 정합성을 확인해주세요.")
            with grp_da:
                st.header("그룹 분석")
                st.write("분석하고자 하는 캠페인을 선택해주세요.")
                if 'description_cmp_detail' in st.session_state.da_cmp_ranking_result.keys():
                    st.write("아래는 " + st.session_state.da_cmp_ranking_result["channel"] + "의 캠페인 목록입니다.")
                    
                    da_selected_campaign = st.selectbox(
                        "캠페인 선택",
                        st.session_state.da_cmp_ranking_result["cmp_df"]["캠페인"].dropna().unique(),
                    )

                    st.session_state.da_grp_ranking_result = {"campaign" : da_selected_campaign}

                    da_filtered_grp_df = st.session_state.df_set["used_media"][(st.session_state.df_set["used_media"]["매체"] == st.session_state.da_cmp_ranking_result["channel"]) & (st.session_state.df_set["used_media"]["캠페인"] == da_selected_campaign)]
                    da_filtered_ga_grp_df = st.session_state.df_set["used_ga"][(st.session_state.df_set["used_ga"]["매체"] == st.session_state.da_cmp_ranking_result["channel"]) & (st.session_state.df_set["used_ga"]["캠페인"] == da_selected_campaign)]

                    st.session_state.da_grp_ranking_result["grp_df"] = da_filtered_grp_df
                    st.session_state.da_grp_ranking_result["ga_grp_df"] = da_filtered_ga_grp_df

                    da_detail_grp_df, da_metric_filtered_detail_grp_df, da_dtl_grp_all_col_list = ch_ranking_writer.ch_ranking_df(
                        da_filtered_grp_df,
                        da_filtered_ga_grp_df,
                        '광고그룹',
                        st.session_state.metric_set,
                        st.session_state.cal_trans_metric_set,
                        st.session_state.trans_metric_set,
                        grouping_period,
                        st.session_state.condition_set,
                    )

                    da_filtered_detail_grp_df = da_metric_filtered_detail_grp_df[da_metric_filtered_detail_grp_df[grouping_period] == st.session_state.period_set["now"]]

                    if len(da_filtered_detail_grp_df) == 0:
                        st.write("이번 기간에는 운영되지 않은 캠페인입니다.")
                    else:
                        da_sorted_grp_df, da_top_grp_num, da_grp_statements = detail_writer.display_top(
                            st.session_state.da_cmp_ranking_result["selected_metrics"],
                            st.session_state.da_cmp_ranking_result["metric_sort_order"],
                            da_filtered_detail_grp_df, 
                            st.session_state.overview_result['overview_df'],
                        )

                        st.session_state.da_grp_ranking_result['top_grp_detail_df'] = da_sorted_grp_df
                        st.session_state.da_grp_ranking_result['top_num_grp_detail'] = da_top_grp_num
                        st.session_state.da_grp_ranking_result['grp_detail_statment'] = da_grp_statements

                        st.write('정렬된 상위 ' + str(da_top_grp_num) + '개 광고그룹')
                        st.write(da_sorted_grp_df)

                        #for statement in grp_statements:
                        #    st.write(statement)

                        try:
                            da_description_grp_detail = detail_writer.writer(da_top_grp_num, da_sorted_grp_df, st.session_state.da_cmp_ranking_result["selected_metrics"],"광고그룹")

                            st.session_state.da_grp_ranking_result['description_grp_detail'] = da_description_grp_detail

                            #st.write(description_grp_detail)
                            bullet_output.display_analysis(da_description_grp_detail, sorted_grp_df.columns.to_list(),"광고그룹")
                        except:
                            st.write("데이터 정합성을 확인해주세요.")
                else:
                    st.write("캠페인 분석 탭을 먼저 실행해주세요.")
            with brnch_da:
                if st.session_state["brnch_dsply"] != 0:
                    for brnch in st.session_state.brnch_ranking_result["sort_order"]:
                        if str(brnch) == '정보없음':
                            continue
                        elif (brnch in da_filtered_type_df["소재구분"].dropna().unique()) and (brnch in da_brnch_list):
                            st.subheader(brnch)
                            st.write(st.session_state.brnch_ranking_result["brnch_overview_df_dic"][brnch])
                            with st.expander("전체 지표 별 변화 문구"):
                                bullet_output.print_dic_bullet(st.session_state.brnch_ranking_result["brnch_overview_st_dic"][brnch])
                            summary_text_4 = st.session_state.brnch_ranking_result['brnch_overview_st_dic_summary'][brnch]['총평'].split('. ')
                            st.write(f"**총평**:")
                            for s in summary_text_4:
                                st.write("- ", s)
                            #bullet_output.print_dic_bullet(st.session_state.brnch_ranking_result["brnch_overview_st_dic_summary"][brnch])
                        else:
                            continue
                else:
                    st.write('매체 데이터에서 소재구분 데이터가 없는 기간입니다.')
            with brnch_dtl_da:
                if st.session_state["brnch_dsply"] == 0:
                    st.write('매체 데이터에서 소재구분 데이터가 없는 기간입니다.')
                else:
                    st.header("소재 종류 분석")
                    st.write("분석하고자 하는 소재 구분을 선택해주세요.")
                    selected_br = st.radio(
                        "소재구분 선택",
                        filtered_type_df["소재구분"].dropna().unique()
                    )
                
                    sort_orders_br = org_sort_orders
                    metrics = st.session_state.overview_result['overview_df'].columns.tolist()

                    for metric in metrics:
                        if metric not in org_sort_orders.keys():
                            sort_orders_br[metric] = False
                        else:
                            pass
                    
                    submit_button_br, sort_columns_br = detail_writer.choose_metric(metrics,1)

                    if submit_button_br:
                        st.session_state["br_current_version"] += 1
                        if st.session_state["br_previous_version"] < 0:
                            st.session_state["br_previous_version"] = 0

                    if (st.session_state["br_previous_version"] >= 0):
                        if (st.session_state["br_previous_version"] != st.session_state["br_current_version"]):

                            filtered_br_df = filtered_type_df[filtered_type_df["소재구분"] == selected_br]
                            filtered_ga_br_df = filtered_ga_type_df[filtered_ga_type_df["소재구분"] == selected_br]

                            detail_df, metric_filtered_detail_df, dtl_all_col_list = ch_ranking_writer.ch_ranking_df(
                                filtered_br_df,
                                filtered_ga_br_df,
                                '소재종류',
                                st.session_state.metric_set,
                                st.session_state.cal_trans_metric_set,
                                st.session_state.trans_metric_set,
                                grouping_period,
                                st.session_state.condition_set,
                            )
                            
                            filtered_detail_df = metric_filtered_detail_df[metric_filtered_detail_df[grouping_period] == st.session_state.period_set["now"]]

                            sorted_df, top_num, br_statements = detail_writer.display_top(
                                sort_columns_br,
                                sort_orders_br,
                                filtered_detail_df, 
                                st.session_state.overview_result['overview_df'],
                            )

                            st.session_state.brnch_detail_result = {'top_brnch_detail_df':sorted_df,'top_num_brnch_detail': top_num, 'brnch_detail_statment':br_statements}

                            st.write('정렬된 상위 ' + str(top_num) + '개 소재종류')
                            st.write(sorted_df)

                            #for statement in br_statements:
                            #    st.write(statement)

                            try:
                                description_brnch_detail = detail_writer.writer(top_num, sorted_df, sort_columns_br, "소재")

                                st.session_state.brnch_detail_result['description_brnch_detail'] = description_brnch_detail

                                #st.write(description_brnch_detail)
                                bullet_output.display_analysis(description_brnch_detail,sorted_df.columns.to_list(), "소재")
                            except:
                                st.session_state.brnch_detail_result['description_brnch_detail'] = "1데이터 정합성을 확인해주세요."
                                st.write("2데이터 정합성을 확인해주세요.")

                        else:
                            st.write('정렬 기준 지표를 선택한 후, 정렬 적용 버튼을 눌러주세요.')
                            if st.session_state.brnch_detail_result is not None:
                                st.write('정렬된 상위 ' + str(st.session_state.brnch_detail_result['top_num_brnch_detail']) + '개 소재종류')
                                st.write(st.session_state.brnch_detail_result['top_brnch_detail_df'])

                                #for statement in st.session_state.brnch_detail_result['brnch_detail_statment']:
                                #    st.write(statement)
                                #st.write(st.session_state.brnch_detail_result['description_brnch_detail'])
                                try:
                                    bullet_output.display_analysis(st.session_state.brnch_detail_result['description_brnch_detail'],st.session_state.brnch_detail_result['top_brnch_detail_df'].columns.to_list(), "소재")
                                except:
                                    st.write("3데이터 정합성을 확인해주세요.")              
            with kwrd_da:
                st.header("키워드별 성과 분석")
                st.write("성과 상위 키워드를 분석합니다.")
                st.write("※ 아래는 이전 선택들과 별개입니다.")
                
                #매체 선택 필터
                can_channel_list = ["선택안함"] + list(da_filtered_type_df["매체"].dropna().unique())
                da_kwrd_selected_channel = st.selectbox(
                        "- **매체 선택**",
                        can_channel_list,
                        index=can_channel_list.index(st.session_state.DA_result["channel"])
                    )
                
                #캠페인 선택 필터
                if da_kwrd_selected_channel != "선택안함":
                    da_kwrd_filtered_cmp_df = da_filtered_type_df[da_filtered_type_df["매체"] == da_kwrd_selected_channel]
                    da_kwrd_selected_cmp = st.selectbox(
                            "- **캠페인 선택**",
                            ["선택안함"] + list(da_kwrd_filtered_cmp_df["캠페인"].dropna().unique()),
                            index=0
                        )
                else:
                    da_kwrd_selected_cmp = st.selectbox(
                            "- **캠페인 선택**",
                            ["선택안함"] + list(da_filtered_type_df["캠페인"].dropna().unique()),
                            index=0
                        )

                #광고그룹 선택 필터
                if (da_kwrd_selected_channel != "선택안함") or (da_kwrd_selected_cmp != "선택안함"):
                    if (da_kwrd_selected_channel != "선택안함") and (da_kwrd_selected_cmp != "선택안함"):
                        da_kwrd_filtered_grp_df = da_filtered_type_df[(da_filtered_type_df["매체"] == da_kwrd_selected_channel) & (da_filtered_type_df["캠페인"] == da_kwrd_selected_cmp)]
                    else:
                        if (da_kwrd_selected_channel != "선택안함"):
                            da_kwrd_filtered_grp_df = da_filtered_type_df[da_filtered_type_df["매체"] == da_kwrd_selected_channel]
                        else:
                            da_kwrd_filtered_grp_df = da_filtered_type_df[da_filtered_type_df["캠페인"] == da_kwrd_selected_cmp]
                    
                    da_kwrd_selected_grp = st.selectbox(
                                "- **광고그룹 선택**",
                                ["선택안함"] + list(da_kwrd_filtered_grp_df["광고그룹"].dropna().unique()),
                                index=0
                            )
                else:
                    da_kwrd_selected_grp = st.selectbox(
                            "- **광고그룹 선택**",
                            ["선택안함"] + list(da_filtered_type_df["광고그룹"].dropna().unique()),
                            index=0
                        )
                
                da_media_df_cleaned = st.session_state.df_set["used_media"].dropna(subset=['소재명/키워드'])
                da_ga_df_cleaned = st.session_state.df_set["used_ga"].dropna(subset=['소재명/키워드'])

                #데이터 필터링
                if (da_kwrd_selected_channel != "선택안함") or (da_kwrd_selected_cmp != "선택안함") or (da_kwrd_selected_grp != "선택안함"):
                    # 필터링 조건 초기화
                    da_conditions_media = [True] * len(da_media_df_cleaned)
                    da_conditions_ga = [True] * len(da_ga_df_cleaned)

                    # 조건에 따라 필터링
                    if da_kwrd_selected_channel != "선택안함":
                        da_conditions_media &= da_media_df_cleaned['매체'] == da_kwrd_selected_channel
                        da_conditions_ga &= da_ga_df_cleaned['매체'] == da_kwrd_selected_channel

                    if da_kwrd_selected_cmp != "선택안함":
                        da_conditions_media &= da_media_df_cleaned['캠페인'] == da_kwrd_selected_cmp
                        da_conditions_ga &= da_ga_df_cleaned['캠페인'] == da_kwrd_selected_cmp

                    if da_kwrd_selected_grp != "선택안함":
                        da_conditions_media &= da_media_df_cleaned['광고그룹'] == da_kwrd_selected_grp
                        da_conditions_ga &= da_ga_df_cleaned['광고그룹'] == da_kwrd_selected_grp

                    # 필터링 적용
                    da_filtered_media_df_cleaned = da_media_df_cleaned[da_conditions_media]
                    da_filtered_ga_df_cleaned = da_ga_df_cleaned[da_conditions_ga]
                else:
                    da_filtered_media_df_cleaned = da_media_df_cleaned
                    da_filtered_ga_df_cleaned = da_ga_df_cleaned



                try:
                    da_detail_kwrd_df, da_metric_filtered_detail_kwrd_df, da_dtl_kwrd_all_col_list = keyword_writer.detail_kwrd_ranking_df(
                                da_filtered_media_df_cleaned,
                                da_filtered_ga_df_cleaned,
                                '소재명/키워드',
                                st.session_state.metric_set,
                                st.session_state.cal_trans_metric_set,
                                st.session_state.trans_metric_set,
                                grouping_period,
                                st.session_state.condition_set,
                            )
                    da_filtered_detail_kwrd_df = da_metric_filtered_detail_kwrd_df[da_metric_filtered_detail_kwrd_df[grouping_period] == st.session_state.period_set["now"]]

                    if not da_filtered_detail_kwrd_df.empty:
                        da_kwrd_ascending_orders = [st.session_state.da_cmp_ranking_result["metric_sort_order"][col] for col in st.session_state.da_cmp_ranking_result["selected_metrics"]]
                        da_sorted_detail_kwrd_df = da_filtered_detail_kwrd_df.sort_values(by="총비용", ascending=False)
                        st.write(da_sorted_detail_kwrd_df)
                        
                        da_kwrd_statements = keyword_writer.writer_new(
                            da_filtered_detail_kwrd_df,
                            st.session_state.da_cmp_ranking_result["selected_metrics"],
                            st.session_state.da_cmp_ranking_result["metric_sort_order"],
                        )
                    else:
                        st.write("이번 기간에는 운영된 소재/키워드가 없습니다.")
                except:
                    st.write("**※※ 매체데이터와 GA 데이터 결합에 문제가 있어, '소재명/키워드'로 필터링된 각각의 데이터를 출력합니다. ※※**")
                    st.write(da_filtered_media_df_cleaned, da_filtered_ga_df_cleaned)
            

    with history_col:
        history = st.tabs(["운영 히스토리"])
        with history[0]:
            filtered_type_df = st.session_state.df_set['used_media']
            filtered_ga_type_df = st.session_state.df_set['used_ga']

            st.write("분석하고자 하는 매체를 선택해주세요.")
            selected_channel = st.selectbox(
                "매체 선택",
                filtered_type_df["매체"].dropna().unique()
            )
            
            st.session_state.history_result["channel"] = selected_channel

            filtered_type_history = st.session_state.df_set['used_history'][st.session_state.df_set['used_history']["매체"] == selected_channel]
            st.write(filtered_type_history)

            st.write("지난 기간 : ", st.session_state.period_set["pre"])
            pre_history = history_writer.writer(
                filtered_type_history,
                grouping_period,
                st.session_state.period_set["pre"])
            st.write(pre_history)

            st.write("이번 기간 : ", st.session_state.period_set["now"])
            now_history = history_writer.writer(
                filtered_type_history,
                grouping_period,
                st.session_state.period_set["now"]
            )
            st.write(now_history)

else:   
    st.write("1. 사이드 바에 매체, GA, 운영 데이터 파일을 업로드하고, 보고서 유형을 선택해 다음 단계 버튼을 눌러주세요.")
    st.write("2. 파일 업로드와 다음 단계 버튼을 누르면, 표에서 확인할 전환 지표를 설정하는 창이 생깁니다.")
    st.write("3. 전환 지표 설정 창에서 전환수로 계산할 전환 지표를 선택 후, 보고서 생성 버튼을 누르면, 보고서 생성이 시작됩니다.")
