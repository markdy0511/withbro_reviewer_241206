from datetime import datetime, timedelta 
import pandas as pd

def get_week_info(date, start_weekday):
    if isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()
        date = date.date()

    # 요일 매핑 (0 = 월요일, 6 = 일요일)
    weekday_dict = {"월요일": 0, "일요일": 6}
    start_weekday_num = weekday_dict[start_weekday]

    # 입력된 날짜의 주 시작일과 종료일 계산
    days_to_subtract = (date.weekday() - start_weekday_num) % 7
    start_of_week = date - timedelta(days=days_to_subtract)
    end_of_week = start_of_week + timedelta(days=6)

    # 해당 주에 속한 각 월의 날짜 수 계산
    day_counts = {}
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        current_month = current_day.month
        day_counts[current_month] = day_counts.get(current_month, 0) + 1

    # 가장 많은 날짜가 포함된 월로 주를 할당
    assigned_month = max(day_counts, key=lambda k: (day_counts[k], k))

    # 해당 월의 첫째 날부터 주차 번호 계산
    first_day_of_month = datetime(start_of_week.year, assigned_month, 1).date()
    days_to_subtract = (first_day_of_month.weekday() - start_weekday_num) % 7
    first_week_start = first_day_of_month - timedelta(days=days_to_subtract)

    week_number = 1
    current_week_start = first_week_start

    while current_week_start < start_of_week:
        # 각 주마다 해당 월에 속한 날짜 수 계산
        day_counts_current_week = {}
        for i in range(7):
            current_day = current_week_start + timedelta(days=i)
            current_month = current_day.month
            day_counts_current_week[current_month] = day_counts_current_week.get(current_month, 0) + 1

        # 해당 월에 4일 이상 포함되면 주차 번호 증가
        if day_counts_current_week.get(assigned_month, 0) >= 4:
            week_number += 1

        current_week_start += timedelta(days=7)

    # 한국어 월 이름 매핑
    month_dict_kr = {
        1: "1월", 2: "2월", 3: "3월", 4: "4월", 5: "5월", 6: "6월",
        7: "7월", 8: "8월", 9: "9월", 10: "10월", 11: "11월", 12: "12월"
    }
    month_name_kr = month_dict_kr[assigned_month]

    return f"{month_name_kr} {week_number}주"

# 주차 계산기
def get_week_info_original(date, start_weekday):

    if isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()
        date = date.date()
    # Define the start of the week (0 = Monday, 6 = Sunday)
    weekday_dict = {"월요일": 0, "일요일": 6}
    start_weekday_num = weekday_dict[start_weekday]
    # Calculate the start of the week for the given date
    start_of_week = date - timedelta(days=(date.weekday() - start_weekday_num) % 7)

    # Get the month and the week number
    month = start_of_week.month
    start_of_month = datetime(start_of_week.year, month, 1).date()
    week_number = ((start_of_week - start_of_month).days // 7) + 1
    
    # Get the month name in Korean for output
    month_dict_kr = {
        1: "1월", 2: "2월", 3: "3월", 4: "4월", 5: "5월", 6: "6월", 
        7: "7월", 8: "8월", 9: "9월", 10: "10월", 11: "11월", 12: "12월"
    }
    month_name_kr = month_dict_kr[month]
    
    return str(month_name_kr)+" "+str(week_number)+"주"

# 월 계산기
def get_month_info(date):
    return date.month

def get_group_kwr(analysis_period):
    #기간 그룹핑용
    if analysis_period == "일간":
        return "일자"
    elif analysis_period == "주간":
        return "주"
    else:
        return "월"