import pandas as pd
from datetime import timedelta
import streamlit as st
import matplotlib.pyplot as plt

def trend_seven(reference_date, df_set, commerce_or_not):
    media_col, ga_col = st.columns(2)
    reference = pd.to_datetime(reference_date, format='%Y-%m-%d')
    media_df = df_set['formatted_media']
    ga_df = df_set['formatted_ga']
    
    filtered_media_df = media_df[(media_df['일자'] >= reference - timedelta(days=7)) & (media_df['일자'] <= reference)]
    filtered_media_df['일자'] = filtered_media_df['일자'].dt.strftime('%Y-%m-%d')

    filtered_ga_df = ga_df[(ga_df['일자'] >= reference - timedelta(days=7)) & (ga_df['일자'] <= reference)]
    filtered_ga_df['일자'] = filtered_ga_df['일자'].dt.strftime('%Y-%m-%d')

    if commerce_or_not == "비커머스":
        grouped_media_df = filtered_media_df.groupby("일자")["DB전환"].sum().reset_index()
        grouped_ga_df = filtered_ga_df.groupby("일자")["DB전환"].sum().reset_index()

        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(grouped_media_df["일자"], grouped_media_df["DB전환"], marker="o", linestyle="-")
        ax1.set_title("Media DB Cov. Trend")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("DB Cov.")
        ax1.grid(True)
        plt.xticks(rotation=45)

        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(grouped_ga_df["일자"], grouped_ga_df["DB전환"], marker="o", linestyle="-")
        ax2.set_title("GA DB Cov. Trend")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("DB Cov.")
        ax2.grid(True)
        plt.xticks(rotation=45)

    else:
        grouped_media_df_cost = filtered_media_df.groupby("일자")["총비용"].sum().reset_index()


        grouped_media_df_revenue = filtered_media_df.groupby("일자")["구매액"].sum().reset_index()
        grouped_ga_df_revenue = filtered_ga_df.groupby("일자")["구매액"].sum().reset_index()

        media_roas = 100 * grouped_media_df_revenue["구매액"] / grouped_media_df_cost["총비용"]
        ga_roas = 100 * grouped_ga_df_revenue["구매액"] / grouped_media_df_cost["총비용"]

        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(grouped_media_df_revenue["일자"], media_roas, marker="o", linestyle="-")
        ax1.set_title("Media ROAS Trend")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("ROAS")
        ax1.grid(True)
        plt.xticks(rotation=45)

        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(grouped_ga_df_revenue["일자"], ga_roas, marker="o", linestyle="-")
        ax2.set_title("GA ROAS Trend")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("ROAS")
        ax2.grid(True)
        plt.xticks(rotation=45)


    with media_col:
        st.pyplot(fig1)
    
    with ga_col:
        st.pyplot(fig2)

    return None