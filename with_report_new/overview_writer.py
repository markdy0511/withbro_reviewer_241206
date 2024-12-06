from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
import streamlit as st
import pandas as pd
from langchain.schema import StrOutputParser
from with_report.grouping import grouped_media, grouped_ga
from with_report.reporting import report_media, report_ga, report_ga_add
from with_report.diff import comparing_df
from with_report.rounding import round_two_axis, round_multi_axis

overview_llm = ChatOpenAI(
    temperature=0.2,
    model = "gpt-4o"
)

def overview_df(media_df, ga_df, metric_set, cal_trans_metric_set, pr_trans_metric_set, group_period, condition_set, period_set):
    grouped_media_df = grouped_media(media_df, metric_set, group_period)
    reported_media_df = report_media(grouped_media_df, metric_set, cal_trans_metric_set, condition_set)

    grouped_ga_df = grouped_ga(ga_df, metric_set, group_period)
    calculated_ga_df = report_ga(grouped_ga_df, metric_set, cal_trans_metric_set, condition_set)
    reported_ga_df = report_ga_add(reported_media_df, calculated_ga_df, condition_set)

    df_combined = pd.concat([reported_media_df, reported_ga_df], axis=1)
    overview_df = comparing_df(df_combined, period_set)


    if condition_set["commerce_or_not"] == '비커머스':
        rounded_overview_df = round_two_axis(overview_df, '증감율', 'CTR', period_set)
    else:
        rounded_overview_df = round_multi_axis(overview_df,  '증감율', ['CTR','ROAS','전환율','GA_ROAS','GA_전환율'], period_set)


    unsel_media_trans_set = set(metric_set['trans_metric']) - set(pr_trans_metric_set['selected_trans_media'])
    unsel_ga_trans_set = set(metric_set['trans_ga_metric']) - set(pr_trans_metric_set['selected_trans_ga'])

    GA_unsel_ga_trans_set = {f"GA_{item}" for item in unsel_ga_trans_set}


    filter_trans = list(unsel_media_trans_set | GA_unsel_ga_trans_set)

    rounded_overview_df_filtered = rounded_overview_df.drop(columns=filter_trans)

    return rounded_overview_df, rounded_overview_df_filtered

def writer(rounded_overview_df, metric_col):
    cost = []
    inflow = []
    media_trans = []
    ga_trans = []

    for col in metric_col:
        if col == "총비용":
            cost.append("총비용")
        elif col in ["노출수", "클릭수", "CTR", "CPC"]:
            inflow.append(col)
            #if col == "CTR":
            #    pass
            #else:
            #    inflow.append(col)
        elif "GA" in col:
            ga_trans.append(col)
        else:
            media_trans.append(col)

    #st.write(cost, inflow, ga_trans, media_trans)
    description = "Periodical change data results:\n\n"
    description += rounded_overview_df.to_string()
    print(description)
    sentences = {}
    if len(rounded_overview_df) == 1:
        sentences = {"데이터 없음":"비교할 수 있는 기간이 없음."}
        descript_raw = {"데이터 없음":"비교할 수 있는 기간이 없음."}
        return sentences, descript_raw
    else:
        previous_period = rounded_overview_df.iloc[0]
        current_period = rounded_overview_df.iloc[1]
        change_period = rounded_overview_df.iloc[2]
        change_rate_period = rounded_overview_df.iloc[3]
        columns = rounded_overview_df.columns[:]

        # Generating the sentences
        for col in columns:
            change = "증가" if change_period[col] > 0 else "감소"
            if change_period[col] != 0 and change_period[col] != None and not(pd.isna(change_period[col])):
                if col in ["총비용", "구매액", "CPC", "CPA", "GA_CPA", "객단가", "GA_객단가"]:
                    sentences[col] = f"{col}은 지난 기간 대비 {abs(change_period[col]):,.0f} 원 {change}하였음. ({previous_period[col]:,.0f} 원 -> {current_period[col]:,.0f} 원, {change_rate_period[col]:,.2f} %)"
                elif col in ["CTR"]:
                    sentences[col] = f"{col}이 지난 기간 대비 {abs(change_period[col]):,.2f} {change}하였음. ({previous_period[col]:,.2f} -> {current_period[col]:,.2f}, {change_rate_period[col]:,.2f} %)"
                elif col in ["ROAS", "전환율","GA_ROAS", "GA_전환율"]:
                    sentences[col] = f"{col}이 지난 기간 대비 {abs(change_period[col]):,.2f} % {change}하였음. ({previous_period[col]:,.2f} % -> {current_period[col]:,.2f} %, {change_rate_period[col]:,.2f} %)"
                elif col in ["노출수", "클릭수"]:
                    change_rate = "증가" if change_rate_period[col] > 0 else "감소"
                    sentences[col] = f"{col}은 지난 기간 대비 {abs(change_rate_period[col]):,.2f} % {change_rate}하였음. ({previous_period[col]:,.2f} % -> {current_period[col]:,.2f} %, {change_rate_period[col]:,.2f} %)"
                else:
                    sentences[col] = f"{col}은 지난 기간 대비 {abs(change_period[col]):,.0f} 건 {change}하였음. ({previous_period[col]:,.0f} 건 -> {current_period[col]:,.0f} 건, {change_rate_period[col]:,.2f} %)"
            elif change_period[col] == None or pd.isna(change_period[col]):
                sentences[col] = f"{col} 데이터가 없음."
            else:
                sentences[col] = f"{col}은 지난 기간과 동일함."
            #sentences.append(sentence)
    #st.write(previous_period,current_period,change_period,columns,sentences)
    descript_raw = {"비용 변화":None, "유입 성과":None, "전환 성과":None,"GA 전환 성과":None, "총평":None}
    descript_raw["비용 변화"] = sentences["총비용"]
    if (change_rate_period["노출수"] > change_rate_period["클릭수"]) and (change_rate_period["노출수"] > 0) and (change_rate_period["클릭수"] > 0):
        descript_raw["유입 성과"] = "클릭수 대비 노출수가 비교적 큰 폭으로 증가하여, " + sentences["CTR"]
    elif (change_rate_period["노출수"] > change_rate_period["클릭수"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["클릭수"] < 0):
        descript_raw["유입 성과"] = "노출수 대비 클릭수가 비교적 작은 폭으로 감소하여, " + sentences["CTR"]
    elif (change_rate_period["노출수"] < change_rate_period["클릭수"]) and (change_rate_period["노출수"] > 0) and (change_rate_period["클릭수"] > 0):
        descript_raw["유입 성과"] = "노출수 대비 클릭수가 비교적 큰 폭으로 증가하여, " + sentences["CTR"]
    elif (change_rate_period["노출수"] < change_rate_period["클릭수"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["클릭수"] < 0):
        descript_raw["유입 성과"] = "클릭수 대비 노출수가 비교적 작은 폭으로 감소하여, " + sentences["CTR"]
    elif change_rate_period["노출수"] > change_rate_period["클릭수"]:
        descript_raw["유입 성과"] = "노출수 증가 및 클릭수 감소로 인해, " + sentences["CTR"]
    elif change_rate_period["노출수"] < change_rate_period["클릭수"]:
        descript_raw["유입 성과"] = "노출수 감소 및 클릭수 증가로 인해, " + sentences["CTR"]
    else:
        descript_raw["유입 성과"] = sentences["CTR"]

    if (change_rate_period["클릭수"] > change_rate_period["총비용"]) and (change_rate_period["클릭수"] > 0) and (change_rate_period["총비용"] > 0):
        descript_raw["유입 성과"] = descript_raw["유입 성과"] + " 또한, " + "총비용 대비 클릭수가 비교적 큰 폭으로 증가하여, " + sentences["CPC"].replace("CPC은", "CPC가")
    elif (change_rate_period["클릭수"] > change_rate_period["총비용"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["클릭수"] < 0):
        descript_raw["유입 성과"] = descript_raw["유입 성과"] + " 또한, " + "클릭수 대비 총비용이 비교적 작은 폭으로 감소하여, " + sentences["CPC"].replace("CPC은", "CPC가")
    elif (change_rate_period["클릭수"] < change_rate_period["총비용"]) and (change_rate_period["클릭수"] > 0) and (change_rate_period["총비용"] > 0):
        descript_raw["유입 성과"] = descript_raw["유입 성과"] + " 또한, " + "클릭수 대비 총비용이 비교적 큰 폭으로 증가하여, " + sentences["CPC"].replace("CPC은", "CPC가")
    elif (change_rate_period["클릭수"] < change_rate_period["총비용"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["클릭수"] < 0):
        descript_raw["유입 성과"] = descript_raw["유입 성과"] + " 또한, " + "총비용 대비 클릭수 비교적 작은 폭으로 감소하여, " + sentences["CPC"].replace("CPC은", "CPC가")
    elif change_rate_period["클릭수"] > change_rate_period["총비용"]:
        descript_raw["유입 성과"] = descript_raw["유입 성과"] + " 또한, " + "클릭수 증가 및 총비용 감소로 인해, " + sentences["CPC"].replace("CPC은", "CPC가")
    elif change_rate_period["클릭수"] < change_rate_period["총비용"]:
        descript_raw["유입 성과"] = descript_raw["유입 성과"] + " 또한, " + "클릭수 감소 및 총비용 증가로 인해, " + sentences["CPC"].replace("CPC은", "CPC가")
    else:
        descript_raw["유입 성과"] = descript_raw["유입 성과"] + ", " + sentences["CPC"]
    
    if "구매" not in media_trans and "GA_구매" not in ga_trans:
        if current_period["전환수"] != 0 and current_period["전환수"] != None and not(pd.isna(current_period["전환수"])):
            descript_raw["전환 성과"] = sentences["전환수"].replace("전환수은", "전환수는")
            for m_metric in media_trans:
                if current_period[m_metric]/current_period["전환수"] > 0.3 and m_metric != "CPA" and m_metric != "전환수":
                    descript_raw["전환 성과"] = descript_raw["전환 성과"] + ", " + sentences[m_metric].replace(m_metric+"은 지난 기간 대비 ", m_metric+"은 ")
                else:
                    pass
            if (change_rate_period["전환수"] > change_rate_period["총비용"]) and (change_rate_period["전환수"] > 0) and (change_rate_period["총비용"] > 0):
                descript_raw["전환 성과"] = descript_raw["전환 성과"] + " 또한, " + "총비용 대비 전환수가 비교적 큰 폭으로 증가하여, " + sentences["CPA"].replace("CPA은", "CPA가")
            elif (change_rate_period["전환수"] > change_rate_period["총비용"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["전환수"] < 0):
                descript_raw["전환 성과"] = descript_raw["전환 성과"] + " 또한, " + "전환수 대비 총비용이 비교적 작은 폭으로 감소하여, " + sentences["CPA"].replace("CPA은", "CPA가")
            elif (change_rate_period["전환수"] < change_rate_period["총비용"]) and (change_rate_period["전환수"] > 0) and (change_rate_period["총비용"] > 0):
                descript_raw["전환 성과"] = descript_raw["전환 성과"] + " 또한, " + "전환수 대비 총비용이 비교적 큰 폭으로 증가하여, " + sentences["CPA"].replace("CPA은", "CPA가")
            elif (change_rate_period["전환수"] < change_rate_period["총비용"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["전환수"] < 0):
                descript_raw["전환 성과"] = descript_raw["전환 성과"] + " 또한, " + "총비용 대비 전환수 비교적 작은 폭으로 감소하여, " + sentences["CPA"].replace("CPA은", "CPA가")
            elif change_rate_period["전환수"] > change_rate_period["총비용"]:
                descript_raw["전환 성과"] = descript_raw["전환 성과"] + " 또한, " + "전환수 증가 및 총비용 감소로 인해, " + sentences["CPA"].replace("CPA은", "CPA가")
            elif change_rate_period["전환수"] < change_rate_period["총비용"]:
                descript_raw["전환 성과"] = descript_raw["전환 성과"] + " 또한, " + "전환수 감소 및 총비용 증가로 인해, " + sentences["CPA"].replace("CPA은", "CPA가")
            else:
                descript_raw["전환 성과"] = descript_raw["전환 성과"] + ", " + sentences["CPA"].replace("CPA은", "CPA가")
        elif current_period["전환수"] == 0:
            descript_raw["전환 성과"] = "전환된 성과가 없음."
        else:
            descript_raw["전환 성과"] = "분석할 전환 데이터가 없음."
        if current_period["GA_전환수"] != 0 and current_period["GA_전환수"] != None and not(pd.isna(current_period["GA_전환수"])):
            descript_raw["GA 전환 성과"] = sentences["GA_전환수"].replace("GA_전환수은", "GA_전환수는")
            for ga_metric in ga_trans:
                if current_period[ga_metric]/current_period["GA_전환수"] > 0.3 and ga_metric != "GA_CPA" and ga_metric != "GA_전환수":
                    descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + ", " + sentences[ga_metric].replace(ga_metric+"은 지난 기간 대비 ", ga_metric+"은 ")
                else:
                    pass
            if (change_rate_period["GA_전환수"] > change_rate_period["총비용"]) and (change_rate_period["GA_전환수"] > 0) and (change_rate_period["총비용"] > 0):
                descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + " 또한, " + "총비용 대비 GA 전환수가 비교적 큰 폭으로 증가하여, " + sentences["GA_CPA"].replace("GA_CPA은", "GA_CPA가")
            elif (change_rate_period["GA_전환수"] > change_rate_period["총비용"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["GA_전환수"] < 0):
                descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + " 또한, " + "GA 전환수 대비 총비용이 비교적 작은 폭으로 감소하여, " + sentences["GA_CPA"].replace("GA_CPA은", "GA_CPA가")
            elif (change_rate_period["GA_전환수"] < change_rate_period["총비용"]) and (change_rate_period["GA_전환수"] > 0) and (change_rate_period["총비용"] > 0):
                descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + " 또한, " + "GA 전환수 대비 총비용이 비교적 큰 폭으로 증가하여, " + sentences["GA_CPA"].replace("GA_CPA은", "GA_CPA가")
            elif (change_rate_period["GA_전환수"] < change_rate_period["총비용"]) and (change_rate_period["노출수"] < 0) and (change_rate_period["GA_전환수"] < 0):
                descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + " 또한, " + "총비용 대비 GA 전환수 비교적 작은 폭으로 감소하여, " + sentences["GA_CPA"].replace("GA_CPA은", "GA_CPA가")
            elif change_rate_period["GA_전환수"] > change_rate_period["총비용"]:
                descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + " 또한, " + "GA 전환수 증가 및 총비용 감소로 인해, " + sentences["GA_CPA"].replace("GA_CPA은", "GA_CPA가")
            elif change_rate_period["GA_전환수"] < change_rate_period["총비용"]:
                descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + " 또한, " + "GA 전환수 감소 및 총비용 증가로 인해, " + sentences["GA_CPA"].replace("GA_CPA은", "GA_CPA가")
            else:
                descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + ", " + sentences["GA_CPA"].replace("GA_CPA은", "GA_CPA가")
        elif current_period["GA_전환수"] == 0:
            descript_raw["GA 전환 성과"] = "전환된 GA 성과가 없음."
        else:
            descript_raw["GA 전환 성과"] = "분석할 GA 전환 데이터가 없음."
    else:
        if current_period["구매"] != 0 and current_period["구매"] != None and not(pd.isna(current_period["구매"])):
            descript_raw["전환 성과"] = sentences["구매액"]
            for m_metric in media_trans:
                if m_metric == "ROAS":
                    descript_raw["전환 성과"] = descript_raw["전환 성과"] + ", " + sentences[m_metric].replace(m_metric+"은 지난 기간 대비 ", m_metric+"가 ")
                elif m_metric == "전환율":
                    descript_raw["전환 성과"] = descript_raw["전환 성과"] + ", " + sentences[m_metric].replace(m_metric+"은 지난 기간 대비 ", m_metric+"이 ")
                else:
                    pass
        elif current_period["구매"] == 0:
            descript_raw["전환 성과"] = "구매 성과가 없음."
        else:
            descript_raw["전환 성과"] = "분석할 구매 데이터가 없음."
        if current_period["GA_구매"] != 0 and current_period["GA_구매"] != None and not(pd.isna(current_period["GA_구매"])):
            descript_raw["GA 전환 성과"] = sentences["GA_구매액"]
            for ga_metric in ga_trans:
                if ga_metric == "GA_ROAS":
                    descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + ", " + sentences[ga_metric].replace(ga_metric+"은 지난 기간 대비 ", ga_metric+"가 ")
                elif ga_metric == "GA_전환율":
                    descript_raw["GA 전환 성과"] = descript_raw["GA 전환 성과"] + ", " + sentences[ga_metric].replace(ga_metric+"은 지난 기간 대비 ", ga_metric+"이 ")
                else:
                    pass
        elif current_period["구매"] == 0:
            descript_raw["GA 전환 성과"] = "GA 구매 성과가 없음."
        else:
            descript_raw["GA 전환 성과"] = "분석할 GA 구매 데이터가 없음."
    #st.write(descript_raw)
    
    en_overview_prompt_v3 = PromptTemplate.from_template(
        """
        You are a performance marketing analyst.
        Please summarize the following {data} into one statement.
        Summarize both positive elements and suggestions for improvements in 30 words only.
        Have to keep causality.
        Using formal language, and output in KOREAN.
        """
    )
    
    
    en_overview_prompt = ChatPromptTemplate.from_messages([
        'system',
        """
        You are a performance marketing analyst. You need to analyze the inflow performance and conversion performance based on the performance data for the following week.

        Check the inflow performance through {inflow}.
        Check the media conversion performance through {trans_media}.
        Check the GA conversion performance through {trans_ga}.

        Focus on summarizing the meaningful absolute values and changes. If there were no significant changes, simply state that they remained stable.

        When using numbers, make sure to show both the absolute value from the previous period and the current period. Example: "Metric name, change rate (previous period absolute value [unit] -> current period absolute value [unit], 00%)". 
        
        - If the change rate is more than 1%, analyze the reasons for the increase or decrease.
        - If costs increase, check whether impressions, clicks, and conversions have also increased.
        - Avoid showing decimal places unless they are meaningful, and discard any zeroes after the decimal point.
        
        Organize the analysis in the following five sections, using formal language, and output in KOREAN, each section has 50 words only:

        '''
        list:  
        [[  
        "전체 요약: 지난 기간 대비 성과 변화 및 주요 KPI (CTR, CPC, CPA 등)의 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%)"/s/s"|
        "유입 성과: 주요 성과 지표 (클릭 수, 노출 수 등)에 대한 변화량을 언급하고, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%)"/s/s"|
        "매체 전환 성과: 매체별 전환 성과 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) 언급 및 전환율 변동에 대한 이유 분석"/s/s"|
        "GA 전환 성과: GA에서 추적된 전환 성과의 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) 및 CPA, 전환 수 변화 분석"/s/s"|
        "총평: 긍정적인 성과와 앞으로 개선해야 할 방향성 제시"/s/s"
        ]]
        '''

        For **inflow performance**, analyze how CTR and CPC have changed and provide reasons for changes in impressions, clicks, and costs.

        For **media and GA conversion performance**, identify how the number of conversions and CPA have changed, focusing on impressions, clicks, and costs.

        Make sure to distinguish between media conversions and GA conversions when explaining.

        In the final section (총평), summarize both positive elements and suggestions for improvements.
        
        Context :
        \n\n{description}
        \n\n{sentences}
        """
    ])
    
    en_overview_prompt_v1 = ChatPromptTemplate.from_messages([
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
        If there are units mentioned in {sentences}, make sure to include the units when referring to them.

        Organize the analysis in the following format, using formal language, and output in KOREAN:

        '''
        list:  
        [[  
        "전체 요약: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "유입 성과: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "매체 전환 성과: 지난 기간 대비 변화, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%)언급 /s/s"|
        "GA 전환 성과: 지난 기간 대비 변화 언급, 변화량 (지난 기간 절대량 [단위] -> 이번 기간 절대량 [단위], 00%) /s/s"|
        "총평: 긍정적인 요소와 앞으로 바꾸면 좋을 방향성 제시 /s/s"
        ]]
        '''

        For inflow performance, analyze how CTR and CPC have changed and provide reasons, focusing on how impressions, clicks, and costs contributed to the changes in CTR and CPC.

        For conversion performance, identify how the number of conversions and CPA have changed. Then analyze the underlying reasons for the changes in impressions, clicks, costs, sign-ups, DB conversions, and potential leads.

        Make sure to distinguish between media conversions and GA conversions when explaining.

        Summarize and create concise sentences for each item, selecting the most relevant metrics or indicators without simply combining sentences.

        Output your analysis in 5 values of list, following the format. If you provide a perfect cause-and-effect explanation, you’ll be rewarded.

        You will face penalties if the data is misread.
        
        let's go!

        Context :
        \n\n{description}
        \n\n{sentences}
        """
    ])

    month_compare_prompt = ChatPromptTemplate.from_messages([
        'system',
        """
        너는 퍼포먼스 마케팅 성과 분석가야.
        다음 주차에 따른 성과 자료를 기반으로 유입 성과와 전환 성과를 분석해야해.

        유입에 대한 성과는 {inflow}를 확인해.
        매체 전환에 대한 성과는 {trans_media}를 확인해.
        GA 전환에 대한 성과는 {trans_ga}를 확인해.

        절대값의 크기, 변화의 크기가 의미있는 것 위주로 정리해줘.
        변화가 크지 않았다면 유지되었다고 이야기하면 돼.

        숫자를 사용할 때는 지난 기간의 절대값과 이번 기간의 절대값을 모두 표시해줘. 예시. "지표 이름, 변화량 (지난 기간의 절대량 [단위] -> 이번 기간의 절대량 [단위], 00%)
        1% 이상의 변화가 있을 때는 유지된 것이 아닌, 어떤 이유로 증가되었는지 또는 감소되었는지를 분석해야해.
        비용의 증가는 노출수, 클릭수, 전환수의 증가를 기대해.
        비용의 증가는 노출수, 클릭수, 전환수의 증가를 기대하는 것 잊지마.
        증감율이 양수면 증가, 음수면 감소야.
        {sentences}에 단위기 있다면, 단위는 꼭 포함해서 언급해줘.

        다음과 같은 양식으로 정리해줘. 존댓말 써.

        '''list:
        [[
        전체 요약 : 지난 기간 대비 변화 언급 /s/s
        유입 성과 : 지난 기간 대비 변화 언급 /s/s
        매체 전환 성과 : 지난 기간 대비 변화 언급 /s/s
        GA 전환 성과 :  지난 기간 대비 변화 언급 /s/s
        총평 : 긍정적인 요소와 앞으로 바꾸면 좋을 방향성 제시 /s/s
        ]]
        '''


        유입 성과는 CTR과 CPC가 얼마나 변하였고, 그에 대한 근거로 노출수와 클릭수, 비용이 어떻게 변화했기에 CTR과 CPC가 그러한 변화를 가지게 되었는지 분석해야해.
        전환 성과는 전환수가 얼마나 변하였고, CPA가 얼마나 변하였는지를 파악하고, 그에 대한 근거로 노출수, 클릭수, 비용, 회원가입, DB전환, 가망에서의 변화를 분석해야해.
        매체 전환과 GA 전환을 구분해서 설명해야해.

        분석 결과를 양식과 같이 5줄로 출력해줘.
        완벽한 인과관계를 설명하면 너에게 보상을 줄게.

        데이터에서 잘못읽으면 패널티가 있어.
    
        let's go!

        Context :
        \n\n{description}
        \n\n{sentences}
    """,]
    )

    comparison_month_chain = en_overview_prompt_v3 | overview_llm | StrOutputParser()
    descript = comparison_month_chain.invoke(
            {"data": descript_raw},
        )
    #descript = comparison_month_chain.invoke({"description": description,"sentences":sentences,"inflow":inflow,"trans_media":media_trans,"trans_ga":ga_trans},)
    descript_raw["총평"] = descript
    descript_result = descript.replace("'''","").replace("[[","").replace("]]","").replace("list:","").replace("\n\n","").replace("```","").replace("[","").replace("]","").replace("/n","").replace(".00","").replace('"',"").replace("|","").split("/s/s")
    for i, sen in enumerate(descript_result):
        descript_result[i] = sen.replace("korean","").replace("markdown","").strip()
    descript_raw["총평"] = str(descript_result[-1])
    #st.write("원본")
    #st.write(descript)
    #st.write("전처리")
    #st.write(descript_result)
    
    return sentences, descript_raw