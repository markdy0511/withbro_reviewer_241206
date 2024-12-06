from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import streamlit as st
import pandas as pd
from langchain.schema import StrOutputParser
from with_report.grouping import grouped_media_with, grouped_ga_with
from with_report.reporting import report_media, report_ga, report_ga_add
from with_report.diff import comparing_df
from with_report.rounding import round_two_axis, round_col_axis, round_multi_axis


overview_llm = ChatOpenAI(
    temperature=0.2,
    model = "gpt-4o"
)

def ch_ranking_df(media_df, ga_df, col_name, metric_set, trans_metric_set, group_period, condition_set):
    grouped_media_df = grouped_media_with(media_df, col_name, metric_set, group_period)
    reported_media_df = report_media(grouped_media_df, metric_set, trans_metric_set, condition_set)

    grouped_ga_df = grouped_ga_with(ga_df, col_name, metric_set, group_period)
    calculated_ga_df = report_ga(grouped_ga_df, metric_set, trans_metric_set, condition_set)
    reported_ga_df = report_ga_add(reported_media_df, calculated_ga_df, condition_set)
 
    df_combined = pd.concat([reported_media_df, reported_ga_df], axis=1)

    df_combined.reset_index(inplace=True)
    df_combined[[col_name, group_period]] = pd.DataFrame(df_combined['index'].tolist(), index=df_combined.index)
    df_combined.drop(columns=['index'], inplace=True)
    # 특정 열을 앞에 오도록 열 순서 재배치
    columns = [col_name, group_period] + [col for col in df_combined.columns if (col != col_name) and (col != group_period)]
    df_combined_re = df_combined[columns]

    rounded_ch_ranking_df = round_col_axis(df_combined_re, 'CTR')
    rounded_ch_ranking_df[col_name] = rounded_ch_ranking_df[col_name].fillna('정보없음')


    return rounded_ch_ranking_df

def display_period_data(period_val,ch_ranking_df, overview_df,col_name,group_period,sort_order):
    #st.subheader(period_val)
    ch_period_df = ch_ranking_df[ch_ranking_df[group_period] == period_val]
    if sort_order is None:
        sorted_ch_period_df = ch_period_df.sort_values(by='전환수', ascending=False)
        ordering = sorted_ch_period_df[col_name].tolist()
    else:
        common_order = [item for item in sort_order if item in ch_period_df[col_name].tolist()]
        sorted_ch_period_df = ch_period_df.set_index(col_name).loc[common_order].reset_index()
        
        remaining_df = ch_period_df[~ch_period_df[col_name].isin(common_order)]
        sorted_ch_period_df = pd.concat([sorted_ch_period_df, remaining_df])
        
        #ordering = sorted_ch_period_df[col_name].tolist()
        ordering = common_order

    row = overview_df.loc[period_val] 
    row_df = pd.DataFrame([row])
    row_df.reset_index(drop=True, inplace=True)

    # Step 3: Concatenate the DataFrame with the extracted row
    period_result = pd.concat([sorted_ch_period_df, row_df], axis=0, ignore_index=True)
    period_result.at[period_result.index[-1],col_name] = '합계'
    #now_description = "This period performance data results:\n\n"
    #now_description += now_week.to_string()

    rounded_period_result = round_col_axis(period_result, 'CTR')


    return rounded_period_result, ordering

def ch_df(ch_ranking_df, col_name, col_value, group_period, period_set, condition_set):
    ch_df = ch_ranking_df[ch_ranking_df[col_name] == str(col_value)]
    ch_df.set_index(group_period, inplace=True)
    ch_df.drop(columns=[col_name], inplace=True)

    overview_ch_df = comparing_df(ch_df, period_set)
    #st.write(overview_ch_df)
    if len(overview_ch_df) == 1:
        rounded_overview_ch_df = round_col_axis(overview_ch_df, 'CTR') #1 줄
    else:
        #rounded_overview_ch_df = round_two_axis(overview_ch_df, '증감율', 'CTR', period_set) #4줄

        if condition_set["commerce_or_not"] == '비커머스':
            rounded_overview_ch_df = round_two_axis(overview_ch_df, '증감율', 'CTR', period_set)
        else:
            rounded_overview_ch_df = round_multi_axis(overview_ch_df,  '증감율', ['CTR','ROAS','전환율','GA_ROAS','GA_전환율'], period_set)

    return rounded_overview_ch_df

def ch_writer(ch_overview_st_dic, metric_col):
    cost = []
    inflow = []
    media_trans = []
    ga_trans = []

    for col in metric_col:
        if col == "총비용":
            cost.append("총비용")
        elif col in ["노출수", "클릭수", "CTR", "CPC"]:
            if col == "CTR":
                pass
            else:
                inflow.append(col)
        elif "GA" in col:
            ga_trans.append(col)
        else:
            media_trans.append(col)
    en_summary_prompt = ChatPromptTemplate.from_messages([
        'system',
        """
        You are a performance marketing analyst. You need to analyze the inflow performance and conversion performance based on the performance data for the following week.

        Check the inflow performance through {inflow}.
        Check the media conversion performance through {trans_media}.
        Check the GA conversion performance through {trans_ga}.

        Focus on summarizing the meaningful absolute values and changes. If there were no significant changes, simply state that they remained stable.

        When using numbers, make sure to show both the absolute value from the previous period and the current period. Example: "Metric name, change rate (previous period absolute value [unit] -> current period absolute value [unit], 00%)".
        If the change is more than 1%, you need to analyze the reasons for the increase or decrease, rather than stating that it remained stable.
        When costs increase, make sure to expect increases in impressions, clicks, and conversions.
        If the change rate is positive, it indicates an increase; if negative, it indicates a decrease.

        Organize the analysis in the following format, using formal language, and output in KOREAN:

        '''list:
        [[
        "매체1: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체2: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체3: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체4: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체5: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체6: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체7: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체8: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"
        ]]
        '''

        For inflow performance, analyze how CTR and CPC have changed and provide reasons, focusing on how impressions, clicks, and costs contributed to the changes in CTR and CPC.

        For conversion performance, identify how the number of conversions and CPA have changed. Then analyze the underlying reasons for the changes in impressions, clicks, costs, sign-ups, DB conversions, and potential leads.

        Make sure to distinguish between media conversions and GA conversions when explaining.

        Summarize and create concise sentences for each item, selecting the most relevant metrics or indicators without simply combining sentences.

        You have to summarize every each channel as length of dictionary.
        
        Each channel should be summarized in a sentence of around 30 characters. If you provide perfect causal analysis, you will be rewarded. Misreading the data will result in penalties.

        You will face penalties if the data is misread.
        
        let's go!

        Context :
        \n\n{dic}
    """,]
    )


    summary_prompt = ChatPromptTemplate.from_messages([
        'system',
        """
        너는 퍼포먼스 마케팅 성과 분석가야.
        다음 매체에 따른 성과 문구를 매체별로 요약 정리해야해.

        숫자를 사용할 때는 지난 기간의 절대값과 이번 기간의 절대값을 모두 표시해줘. 예시. 절대값(지난 기간 -> 이번 기간, 00%)
        1% 이상의 변화가 있을 때는 유지된 것이 아닌, 어떤 이유로 증가되었는지 또는 감소되었는지를 분석해야해.
        비용의 증가는 노출수, 클릭수, 전환수의 증가를 기대해.
        비용의 증가는 노출수, 클릭수, 전환수의 증가를 기대하는 것 잊지마.
        증감율이 양수면 증가, 음수면 감소야.

        다음과 같은 양식으로 정리해줘. 존댓말 써. 각 문장은 하였습니다로 끝내.

        '''list:
        [[
        매체1: 지난 기간 대비 변화 언급 /s/s
        매체2: 지난 기간 대비 변화 언급 /s/s
        매체3: 지난 기간 대비 변화 언급 /s/s
        매체4: 지난 기간 대비 변화 언급 /s/s
        매체5: 지난 기간 대비 변화 언급 /s/s
        매체6: 지난 기간 대비 변화 언급 /s/s
        매체7: 지난 기간 대비 변화 언급 /s/s
        매체8: 지난 기간 대비 변화 언급 /s/s
        ]]
        '''


        유입 성과는 CTR과 CPC가 얼마나 변하였고, 그에 대한 근거로 노출수와 클릭수, 비용이 어떻게 변화했기에 CTR과 CPC가 그러한 변화를 가지게 되었는지 분석해야해.
        전환 성과는 전환수가 얼마나 변하였고, CPA가 얼마나 변하였는지를 파악하고, 그에 대한 근거로 노출수, 클릭수, 비용, 회원가입, DB전환, 가망에서의 변화를 분석해야해.
        매체 전환과 GA 전환을 구분해서 설명해야해.

        분석 결과를 양식과 같이 매체 수만큼의 줄 수로 출력해줘.
        한 줄 당 30자 내외로 출력해줘.
        완벽한 인과관계를 설명하면 너에게 보상을 줄게.

        데이터에서 잘못읽으면 패널티가 있어.
    
        let's go!

        Context :
        \n\n{dic}
    """,]
    )

    ch_summary_chain = en_summary_prompt | overview_llm | StrOutputParser()
    with st.status("매체별 분석...") as status: 
        descript = ch_summary_chain.invoke(
            {"dic":ch_overview_st_dic,"inflow":inflow,"trans_media":media_trans,"trans_ga":ga_trans},
        )
    
    descript_result = descript.replace("'''","").replace("[[","").replace("]]","").replace("list:","").replace("\n\n","").replace("```","").replace("[","").replace("]","").replace("/n","").replace(".00","").replace('"',"").replace("|","").split("/s/s")
    for i, sen in enumerate(descript_result):
        descript_result[i] = sen.strip()


    return descript_result