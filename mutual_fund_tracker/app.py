import streamlit as st
from modules.mf_tracker import MutualFundAllocationTracker
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

def main():
    st.title("Mutual Fund Allocation Tracker")
    st.write("Track changes in mutual fund NAV over a specified date range and view Average AUM data.")

    # Initialize the tracker
    tracker = MutualFundAllocationTracker()

    # User inputs
    fund_name = st.text_input("Enter Mutual Fund Name:")
    start_date = st.date_input("Select Start Date:", value=datetime(2020, 1, 1))
    end_date = st.date_input("Select End Date:", value=datetime(2020, 3, 31))
    quarter = st.selectbox("Select Quarter for AUM Data:", 
                           ["January - March 2020", "April - June 2020", "July - September 2020", "October - December 2020", 
                            "January - March 2021", "April - June 2021", "July - September 2021", "October - December 2021"])

    if st.button("Get Data"):
        try:
            # Fetch Fund Details
            scheme_code, full_name = tracker.get_fund_details(fund_name)
            st.success(f"Found Fund: {full_name} (Scheme Code: {scheme_code})")

            # Fetch Historical NAV Data
            historical_data = tracker.fetch_historical_data(scheme_code, start_date, end_date)
            st.subheader("Historical NAV Data")
            st.write(historical_data)

            # Calculate Month-over-Month Changes
            monthly_changes = tracker.calculate_changes(historical_data)
            st.subheader("Month-over-Month Changes")
            st.write(monthly_changes)

            # Plot NAV Percentage Change
            st.subheader("NAV Percentage Change Over Time")
            plt.figure(figsize=(10, 6))
            plt.plot(monthly_changes["month"].dt.to_timestamp(), monthly_changes["percentage_change"], marker="o")
            plt.title("Month-over-Month NAV Percentage Changes")
            plt.xlabel("Month")
            plt.ylabel("Percentage Change (%)")
            plt.grid()
            st.pyplot(plt)

            # Fetch and Display AUM Data
            aum_data = tracker.get_average_aum(quarter, as_json=False)  # Get raw data (not JSON)
            aum_df = pd.DataFrame(aum_data)  # Convert to DataFrame
            st.subheader(f"AUM Data for {quarter}")
            st.dataframe(aum_df)  # Display the data as a table

        except ValueError as e:
            st.error(e)

if __name__ == "__main__":
    main()
