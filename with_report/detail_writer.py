from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
import streamlit as st
from langchain.schema import StrOutputParser
import pandas as pd

overview_llm = ChatOpenAI(
    temperature=0.2,
    model = "gpt-4o"
)


def choose_metric(metric, i):
    with st.form(key='sort_form_br_'+str(i)):
        sort_columns = st.multiselect('가장 먼저 정렬하고 싶은 순서대로 정렬할 기준을 선택하세요 (여러 개 선택 가능):', metric)
        
        # 폼 제출 버튼
        submit_button = st.form_submit_button(label='정렬 적용')

    return submit_button, sort_columns

def generate_statements(df, now_ch_cmp_week, metrics, top_num):
    statements = []
        # Statements for sum metrics

    metrics = [element for element in metrics if (element != '총비용') and (element != '전환수')]
    for metric in metrics:
        if metric in ['CPA', 'CPC', 'CTR', 'GA_CPA']:
            if metric == 'CPA' or metric == 'GA_CPA':
                top_10_cost = df['총비용'].sum()
                top_10_acquisitions = df['전환수'].sum()
                total_cost = now_ch_cmp_week['총비용']
                total_acquisitions = now_ch_cmp_week['전환수']
                top_10_metric = top_10_cost / top_10_acquisitions if top_10_acquisitions != 0 else 0
                total_metric = total_cost / total_acquisitions if total_acquisitions != 0 else 0
            elif metric == 'CPC':
                top_10_cost = df['총비용'].sum()
                top_10_clicks = df['클릭수'].sum()
                total_cost = now_ch_cmp_week['총비용']
                total_clicks = now_ch_cmp_week['클릭수']
                top_10_metric = top_10_cost / top_10_clicks if top_10_clicks != 0 else 0
                total_metric = total_cost / total_clicks if total_clicks != 0 else 0
            elif metric == 'CTR':
                top_10_clicks = df['클릭수'].sum()
                top_10_impressions = df['노출수'].sum()
                total_clicks = now_ch_cmp_week['클릭수']
                total_impressions = now_ch_cmp_week['노출수']
                top_10_metric = (top_10_clicks / top_10_impressions) * 100 if top_10_impressions != 0 else 0
                total_metric = (total_clicks / total_impressions) * 100 if total_impressions != 0 else 0

            ratio = round((top_10_metric - total_metric),2)
            statement = f"정렬된 상위 {top_num}개의 {metric} ({top_10_metric:.2f})는 당 기간 전체 {metric} ({total_metric:.2f})보다 {ratio}만큼 차이가 있습니다."
            statements.append(statement)
        else:
            top_10_sum = df[metric].sum()
            total_sum = now_ch_cmp_week[metric]
            ratio = round((top_10_sum / total_sum) * 100, 2)
            statement = f"정렬된 상위 {top_num}개의 {metric} ({top_10_sum:,.0f})는 당 기간 전체 {metric} ({total_sum:,.0f})의 {ratio}% 입니다."
            statements.append(statement)

    return statements

def display_top(sort_columns, sort_orders, detail_df, overview_df):
    ascending_orders = [sort_orders[col] for col in sort_columns]
    filtered_overview_df = overview_df.iloc[1]
    # 데이터 프레임 정렬
    num_data = len(detail_df)
    if num_data >= 10:
        sorted_df = detail_df.sort_values(by=sort_columns, ascending=ascending_orders).head(10)
    else:
        sorted_df = detail_df.sort_values(by=sort_columns, ascending=ascending_orders).head(num_data)

    top_num = len(sorted_df)
    br_statements = generate_statements(sorted_df, filtered_overview_df, sort_columns, top_num)

    # 값 컬럼을 기준으로 내림차순 정렬 후 상위 10개의 합 계산
    top_10_cost_sum = sorted_df['총비용'].sum()
    total_cost_sum = filtered_overview_df['총비용']
    ratio_cost = round((top_10_cost_sum / total_cost_sum) * 100, 2)

    top_10_cv_sum = sorted_df['전환수'].sum()
    total_cv_sum = filtered_overview_df['전환수']
    ratio_cv = round((top_10_cv_sum / total_cv_sum) * 100, 2)

    cost_statement = "정렬된 상위 " +str(top_num) + " 개의 총비용("+"{:,.0f}".format(top_10_cost_sum)+"원)"+ "은 당 기간 전체 집행 비용("+"{:,.0f}".format(total_cost_sum)+"원)의 "+str(ratio_cost)+"% 입니다."
    cv_statement = "정렬된 상위 " +str(top_num) + " 개의 전환수("+"{:,.0f}".format(top_10_cv_sum)+"건)는 당 기간 전체 전환수("+"{:,.0f}".format(total_cv_sum)+"건)의 "+str(ratio_cv)+"% 입니다."

    br_statements.insert(0,cv_statement)
    br_statements.insert(0,cost_statement)    

    return sorted_df, top_num, br_statements

def writer(top_num, detail_df, sort_columns):

    index_target = detail_df.columns[0]
    detail_df = detail_df.set_index(index_target)
    columns = detail_df.columns[1:]
    sentences = {"비용 분석":{}, "유입 성과":{}, "전환 성과":{},"GA 전환 성과":{}}


    total_sum = detail_df['총비용'].sum(skipna=True)
    max_value = detail_df['총비용'].max()  # 최대값
    min_value = detail_df['총비용'].min()  # 최소값
    max_index = detail_df['총비용'].idxmax()  # 최대값 인덱스
    min_index = detail_df['총비용'].idxmin()  # 최소값 인덱스

            # NaN 값의 인덱스
    nan_indices = detail_df[detail_df['총비용'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

    max_CTR = detail_df['CTR'].max()  # 최대값
    min_CTR = detail_df['CTR'].min()  # 최소값
    max_CTR_index = detail_df['CTR'].idxmax()  # 최대값 인덱스
    min_CTR_index = detail_df['CTR'].idxmin()  # 최소값 인덱스

    # NaN 값의 인덱스
    nan_CTR_indices = detail_df[detail_df['CTR'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

    max_CPC = detail_df['CPC'].max()  # 최대값
    min_CPC = detail_df['CPC'].min()  # 최소값
    max_CPC_index = detail_df['CPC'].idxmax()  # 최대값 인덱스
    min_CPC_index = detail_df['CPC'].idxmin()  # 최소값 인덱스

    # NaN 값의 인덱스
    nan_CPC_indices = detail_df[detail_df['CPC'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

    if "구매" not in columns:
        max_CPA = detail_df['CPA'].max()  # 최대값
        min_CPA = detail_df['CPA'].min()  # 최소값
        max_CPA_index = detail_df['CPA'].idxmax()  # 최대값 인덱스
        min_CPA_index = detail_df['CPA'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_CPA_indices = detail_df[detail_df['CPA'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_COV = detail_df['전환수'].max()  # 최대값
        min_COV = detail_df['전환수'].min()  # 최소값
        max_COV_index = detail_df['전환수'].idxmax()  # 최대값 인덱스
        min_COV_index = detail_df['전환수'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_COV_indices = detail_df[detail_df['전환수'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_GACPA = detail_df['GA_CPA'].max()  # 최대값
        min_GACPA = detail_df['GA_CPA'].min()  # 최소값
        max_GACPA_index = detail_df['GA_CPA'].idxmax()  # 최대값 인덱스
        min_GACPA_index = detail_df['GA_CPA'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_GACPA_indices = detail_df[detail_df['GA_CPA'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_GACOV = detail_df['GA_전환수'].max()  # 최대값
        min_GACOV = detail_df['GA_전환수'].min()  # 최소값
        max_GACOV_index = detail_df['GA_전환수'].idxmax()  # 최대값 인덱스
        min_GACOV_index = detail_df['GA_전환수'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_GACOV_indices = detail_df[detail_df['GA_전환수'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트
    else:
        max_p = detail_df['구매액'].max()  # 최대값
        min_p = detail_df['구매액'].min()  # 최소값
        max_p_index = detail_df['구매액'].idxmax()  # 최대값 인덱스
        min_p_index = detail_df['구매액'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_p_indices = detail_df[detail_df['구매액'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_ROAS = detail_df['ROAS'].max()  # 최대값
        min_ROAS = detail_df['ROAS'].min()  # 최소값
        max_ROAS_index = detail_df['ROAS'].idxmax()  # 최대값 인덱스
        min_ROAS_index = detail_df['ROAS'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_ROAS_indices = detail_df[detail_df['ROAS'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_COVR = detail_df['전환율'].max()  # 최대값
        min_COVR = detail_df['전환율'].min()  # 최소값
        max_COVR_index = detail_df['전환율'].idxmax()  # 최대값 인덱스
        min_COVR_index = detail_df['전환율'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_COVR_indices = detail_df[detail_df['전환율'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_GAp = detail_df['GA_구매액'].max()  # 최대값
        min_GAp = detail_df['GA_구매액'].min()  # 최소값
        max_GAp_index = detail_df['GA_구매액'].idxmax()  # 최대값 인덱스
        min_GAp_index = detail_df['GA_구매액'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_GAp_indices = detail_df[detail_df['GA_구매액'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_ROAS = detail_df['ROAS'].max()  # 최대값
        min_ROAS = detail_df['ROAS'].min()  # 최소값
        max_ROAS_index = detail_df['ROAS'].idxmax()  # 최대값 인덱스
        min_ROAS_index = detail_df['ROAS'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_ROAS_indices = detail_df[detail_df['ROAS'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트

        max_GACOVR = detail_df['GA_전환율'].max()  # 최대값
        min_GACOVR = detail_df['GA_전환율'].min()  # 최소값
        max_GACOVR_index = detail_df['GA_전환율'].idxmax()  # 최대값 인덱스
        min_GACOVR_index = detail_df['GA_전환율'].idxmin()  # 최소값 인덱스

        # NaN 값의 인덱스
        nan_GACOVR_indices = detail_df[detail_df['GA_전환율'].isna()].index.tolist()  # NaN 값이 있는 인덱스 리스트




    # "비용 분석" section
    if not pd.isna(total_sum):
        sentences["비용 분석"]["전체 비용"] = f"해당 소재 구분에서 사용된 비용은 {total_sum.round(0)} 원 입니다."
        sentences["비용 분석"]["가장 비용이 많이 사용된 소재"] = (
            f"가장 비용을 많이 사용한 소재 종류는 {max_index} 이며, {max_value} 원 "
            f"({((max_value / total_sum) * 100).round(2)}%) 사용하였습니다."
        )
        sentences["비용 분석"]["가장 비용이 적게 사용된 소재"] = (
            f"가장 비용을 적게 사용한 소재 종류는 {min_index} 이며, {min_value} 원 "
            f"({((min_value / total_sum) * 100).round(2)}%) 사용하였습니다."
        )
    else:
        sentences["비용 분석"]["데이터 없음"] = "해당 소재 구분으로 활용된 데이터가 없습니다."

    # "유입 성과" section
    if not pd.isna(max_CPC):
        sentences["유입 성과"]["가장 CPC가 높은 소재"] = (
            f"가장 CPC가 높은 소재 종류는 {max_CPC_index} 이며, {max_CPC} 원 입니다."
        )
        sentences["유입 성과"]["가장 CPC가 낮은 소재"] = (
            f"가장 CPC가 낮은 소재 종류는 {min_CPC_index} 이며, {min_CPC} 원 입니다."
        )
    else:
        sentences["유입 성과"]["데이터 없음"] = "해당 소재 구분으로 활용된 데이터가 없습니다."

    if not pd.isna(max_CTR):
        sentences["유입 성과"]["가장 CTR이 높은 소재"] = (
            f"가장 CTR이 높은 소재 종류는 {max_CTR_index} 이며, {max_CTR} 입니다."
        )
        sentences["유입 성과"]["가장 CTR이 낮은 소재"] = (
            f"가장 CTR이 낮은 소재 종류는 {min_CTR_index} 이며, {min_CTR} 입니다."
        )
    else:
        sentences["유입 성과"]["CTR 데이터 없음"] = "해당 소재 구분으로 활용된 CTR 데이터가 없습니다."

    # "전환 성과" section based on the presence of "구매"
    if "구매" not in columns:
        if not pd.isna(max_CPA):
            sentences["전환 성과"]["가장 CPA가 높은 소재"] = (
                f"가장 CPA가 높은 소재 종류는 {max_CPA_index} 이며, {max_CPA} 원 입니다."
            )
            sentences["전환 성과"]["가장 CPA가 낮은 소재"] = (
                f"가장 CPA가 낮은 소재 종류는 {min_CPA_index} 이며, {min_CPA} 원 입니다."
            )
        else:
            sentences["전환 성과"]["CPA 데이터 없음"] = "해당 소재 구분으로 활용된 CPA 데이터가 없습니다."

        if not pd.isna(max_COV):
            sentences["전환 성과"]["가장 전환수가 높은 소재"] = (
                f"가장 전환수가 높은 소재 종류는 {max_COV_index} 이며, {max_COV} 건 입니다."
            )
            sentences["전환 성과"]["가장 전환수가 낮은 소재"] = (
                f"가장 전환수가 낮은 소재 종류는 {min_COV_index} 이며, {min_COV} 건 입니다."
            )
        else:
            sentences["전환 성과"]["전환수 데이터 없음"] = "해당 소재 구분으로 활용된 전환수 데이터가 없습니다."
    else:
        if not pd.isna(max_p):
            sentences["전환 성과"]["가장 구매액이 높은 소재"] = (
                f"가장 구매액이 높은 소재 종류는 {max_p_index} 이며, {max_p} 원 입니다."
            )
            sentences["전환 성과"]["가장 구매액이 낮은 소재"] = (
                f"가장 구매액이 낮은 소재 종류는 {min_p_index} 이며, {min_p} 원 입니다."
            )
        else:
            sentences["전환 성과"]["구매액 데이터 없음"] = "해당 소재 구분으로 활용된 구매액 데이터가 없습니다."

        if not pd.isna(max_ROAS):
            sentences["전환 성과"]["가장 ROAS가 높은 소재"] = (
                f"가장 ROAS가 높은 소재 종류는 {max_ROAS_index} 이며, {max_ROAS} % 입니다."
            )
            sentences["전환 성과"]["가장 ROAS가 낮은 소재"] = (
                f"가장 ROAS가 낮은 소재 종류는 {min_ROAS_index} 이며, {min_ROAS} % 입니다."
            )
        else:
            sentences["전환 성과"]["ROAS 데이터 없음"] = "해당 소재 구분으로 활용된 ROAS 데이터가 없습니다."
        if not pd.isna(max_COVR):
            sentences["전환 성과"]["가장 전환율이 높은 소재"] = (
                f"가장 전환율이 높은 소재 종류는 {max_COVR_index} 이며, {max_COVR} % 입니다."
            )
            sentences["전환 성과"]["가장 전환율이 낮은 소재"] = (
                f"가장 전환율이 낮은 소재 종류는 {min_COVR_index} 이며, {min_COVR} % 입니다."
            )
        else:
            sentences["전환 성과"]["전환율 데이터 없음"] = "해당 소재 구분으로 활용된 전환율 데이터가 없습니다."


    # "GA 전환 성과" section based on the presence of "구매"
    if "GA_구매" not in columns:
        if not pd.isna(max_GACPA):
            sentences["GA 전환 성과"]["가장 GA CPA가 높은 소재"] = (
                f"가장 GA CPA가 높은 소재 종류는 {max_GACPA_index} 이며, {max_GACPA} 원 입니다."
            )
            sentences["GA 전환 성과"]["가장 GA CPA가 낮은 소재"] = (
                f"가장 GA CPA가 낮은 소재 종류는 {min_GACPA_index} 이며, {min_GACPA} 원 입니다."
            )
        else:
            sentences["GA 전환 성과"]["GA CPA 데이터 없음"] = "해당 소재 구분으로 활용된 GA CPA 데이터가 없습니다."

        if not pd.isna(max_GACOV):
            sentences["GA 전환 성과"]["가장 GA 전환수가 높은 소재"] = (
                f"가장 GA 전환수가 높은 소재 종류는 {max_GACOV_index} 이며, {max_GACOV} 건 입니다."
            )
            sentences["GA 전환 성과"]["가장 GA 전환수가 낮은 소재"] = (
                f"가장 GA 전환수가 낮은 소재 종류는 {min_GACOV_index} 이며, {min_GACOV} 건 입니다."
            )
        else:
            sentences["GA 전환 성과"]["GA 전환수 데이터 없음"] = "해당 소재 구분으로 활용된 GA 전환수 데이터가 없습니다."
    else:
        if not pd.isna(max_GAp):
            sentences["GA 전환 성과"]["가장 GA 구매액이 높은 소재"] = (
                f"가장 GA 구매액이 높은 소재 종류는 {max_GAp_index} 이며, {max_GAp} 원 입니다."
            )
            sentences["GA 전환 성과"]["가장 GA 구매액이 낮은 소재"] = (
                f"가장 GA 구매액이 낮은 소재 종류는 {min_GAp_index} 이며, {min_GAp} 원 입니다."
            )
        else:
            sentences["GA 전환 성과"]["GA 구매액 데이터 없음"] = "해당 소재 구분으로 활용된 GA 구매액 데이터가 없습니다."

        if not pd.isna(max_ROAS):
            sentences["GA 전환 성과"]["가장 GA ROAS가 높은 소재"] = (
                f"가장 GA ROAS가 높은 소재 종류는 {max_ROAS_index} 이며, {max_ROAS} % 입니다."
            )
            sentences["GA 전환 성과"]["가장 GA ROAS가 낮은 소재"] = (
                f"가장 GA ROAS가 낮은 소재 종류는 {min_ROAS_index} 이며, {min_ROAS} % 입니다."
            )
        else:
            sentences["GA 전환 성과"]["GA ROAS 데이터 없음"] = "해당 소재 구분으로 활용된 GA ROAS 데이터가 없습니다."
        if not pd.isna(max_COVR):
            sentences["GA 전환 성과"]["가장 GA 전환율이 높은 소재"] = (
                f"가장 GA 전환율이 높은 소재 종류는 {max_COVR_index} 이며, {max_COVR} % 입니다."
            )
            sentences["GA 전환 성과"]["가장 GA 전환율이 낮은 소재"] = (
                f"가장 GA 전환율이 낮은 소재 종류는 {min_COVR_index} 이며, {min_COVR} % 입니다."
            )
        else:
            sentences["GA 전환 성과"]["GA 전환율 데이터 없음"] = "해당 소재 구분으로 활용된 GA 전환율 데이터가 없습니다."

    en_br_prompt = PromptTemplate.from_template(
        """
        You are a performance marketing analyst.
        Please summarize the following {data} into one statement.
        Summarize both positive elements and suggestions for improvements in 30 words only.
        Have to keep causality.
        Using formal language, and output in KOREAN.
        """
    )


    metric_str = 'and'.join(str(x) for x in sort_columns)
    br_description = "Top " +str(top_num) + " branches sorted by " + metric_str + ":\n\n"
    br_description += detail_df.to_string()

    br_prompt = ChatPromptTemplate.from_messages([
        'system',
        """
        너는 퍼포먼스 마케팅 성과 분석가야.
        각 소재종류의 성과를 요약해야해.

        유입 성과는 CTR과 CPC가 얼마나 변하였고, 그에 대한 근거로 노출수와 클릭수, 비용이 어떻게 변화했기에 CTR과 CPC가 그러한 변화를 가지게 되었는지 분석해야해.
        전환 성과는 전환수가 얼마나 변하였고, CPA가 얼마나 변하였는지를 파악하고, 그에 대한 근거로 노출수, 클릭수, 비용, 회원가입, DB전환, 가망에서의 변화를 분석해야해.
        매체 전환과 GA 전환을 구분해서 설명해야해.

        완벽한 인과관계를 설명하면 너에게 보상을 줄게.
        종합 분석을 항상 먼저 알려줘.

        데이터에서 잘못읽으면 패널티가 있어.
    
        let's go!

        Context :
        상위 {n}개의 분과구분에 대한 성과 데이터야.
        \n\n{br_per}
    """,]
    )

    br_chain = en_br_prompt | overview_llm | StrOutputParser()
    with st.status("분과구분별 분석...") as status:
        descript_br_d = br_chain.invoke(
            {"data":sentences},
        )

    descript_br_d_result = descript_br_d.replace(".0","")
    sentences["종합 분석"] = descript_br_d_result

    return sentences