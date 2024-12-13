import streamlit as st

def print_bullet(statement):
    #sentences = statement.split('.\n')
    #bullet_list = "<ul>" + "".join(f"<li>{sentence}</li>" for sentence in statement if sentence) + "</ul>"
    bullet_list = "<ul>" + "".join(f"<li>{sentence}</li>" if not sentence.endswith('.') else f"<li>{sentence}</li>" for sentence in statement if sentence) + "</ul>"
    st.markdown(bullet_list, unsafe_allow_html=True)

    return None

def print_dic_bullet(dic):
    for key, value in dic.items():
         st.write(f"- **{key}**: {value}")

    return None

def display_analysis(data, col, criteria):

    st.write("## 종합 분석")
    st.write(f"- {data['종합 분석']}")

    st.write("## 비용 분석")
    st.write(f"- **전체 비용**: {data['비용 분석']['전체 비용']}")
    st.write(f"- **가장 비용이 많이 사용된 {criteria}**: {data['비용 분석'][f'가장 비용이 많이 사용된 {criteria}']}")
    st.write(f"- **가장 비용이 적게 사용된 {criteria}**: {data['비용 분석'][f'가장 비용이 적게 사용된 {criteria}']}")

    st.write("## 유입 성과")
    st.write(f"- **가장 CPC가 높은 {criteria}**: {data['유입 성과'][f'가장 CPC가 높은 {criteria}']}")
    st.write(f"- **가장 CPC가 낮은 {criteria}**: {data['유입 성과'][f'가장 CPC가 낮은 {criteria}']}")
    st.write(f"- **가장 CTR이 높은 {criteria}**: {data['유입 성과'][f'가장 CTR이 높은 {criteria}']}")
    st.write(f"- **가장 CTR이 낮은 {criteria}**: {data['유입 성과'][f'가장 CTR이 낮은 {criteria}']}")

    if "구매" not in col:
        st.write("## 전환 성과")
        st.write(f"- **가장 CPA가 높은 {criteria}**: {data['전환 성과'][f'가장 CPA가 높은 {criteria}']}")
        st.write(f"- **가장 CPA가 낮은 {criteria}**: {data['전환 성과'][f'가장 CPA가 낮은 {criteria}']}")
        st.write(f"- **가장 전환수가 높은 {criteria}**: {data['전환 성과'][f'가장 전환수가 높은 {criteria}']}")
        st.write(f"- **가장 전환수가 낮은 {criteria}**: {data['전환 성과'][f'가장 전환수가 낮은 {criteria}']}")

        st.write("## GA 전환 성과")
        st.write(f"- **가장 GA CPA가 높은 {criteria}**: {data['GA 전환 성과'][f'가장 GA CPA가 높은 {criteria}']}")
        st.write(f"- **가장 GA CPA가 낮은 {criteria}**: {data['GA 전환 성과'][f'가장 GA CPA가 낮은 {criteria}']}")
        st.write(f"- **가장 GA 전환수가 높은 {criteria}**: {data['GA 전환 성과'][f'가장 GA 전환수가 높은 {criteria}']}")
        st.write(f"- **가장 GA 전환수가 낮은 {criteria}**: {data['GA 전환 성과'][f'가장 GA 전환수가 낮은 {criteria}']}")
    else:
        st.write("## 전환 성과")
        st.write(f"- **가장 구매액이 높은 {criteria}**: {data['전환 성과'][f'가장 구매액이 높은 {criteria}']}")
        st.write(f"- **가장 구매액이 낮은 {criteria}**: {data['전환 성과'][f'가장 구매액이 낮은 {criteria}']}")
        st.write(f"- **가장 ROAS가 높은 {criteria}**: {data['전환 성과'][f'가장 ROAS가 높은 {criteria}']}")
        st.write(f"- **가장 ROAS가 낮은 {criteria}**: {data['전환 성과'][f'가장 ROAS가 낮은 {criteria}']}")
        st.write(f"- **가장 전환율이 높은 {criteria}**: {data['전환 성과'][f'가장 전환율이 높은 {criteria}']}")
        st.write(f"- **가장 전환율이 낮은 {criteria}**: {data['전환 성과'][f'가장 전환율이 낮은 {criteria}']}")

        st.write("## GA 전환 성과")
        st.write(f"- **가장 GA 구매액이 높은 {criteria}**: {data['GA 전환 성과'][f'가장 GA 구매액이 높은 {criteria}']}")
        st.write(f"- **가장 GA 구매액이 낮은 {criteria}**: {data['GA 전환 성과'][f'가장 GA 구매액이 낮은 {criteria}']}")
        st.write(f"- **가장 GA ROAS가 높은 {criteria}**: {data['GA 전환 성과'][f'가장 GA ROAS가 높은 {criteria}']}")
        st.write(f"- **가장 GA ROAS가 낮은 {criteria}**: {data['GA 전환 성과'][f'가장 GA ROAS가 낮은 {criteria}']}")
        st.write(f"- **가장 GA 전환율이 높은 {criteria}**: {data['전환 성과'][f'가장 GA 전환율이 높은 {criteria}']}")
        st.write(f"- **가장 GA 전환율이 낮은 {criteria}**: {data['전환 성과'][f'가장 GA 전환율이 낮은 {criteria}']}")
    

    return None