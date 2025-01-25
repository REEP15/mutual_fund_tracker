from mftool import Mftool
import pandas as pd
import requests
from bs4 import BeautifulSoup

class MutualFundAllocationTracker:
    def __init__(self):
        self.mf_tool = Mftool()

    def get_fund_details(self, fund_name):
        all_funds = self.mf_tool.get_scheme_codes()
        for code, name in all_funds.items():
            if fund_name.lower() in name.lower():
                return code, name
        raise ValueError(f"Fund '{fund_name}' not found!")

    def fetch_historical_data(self, scheme_code, start_date, end_date):
        raw_data = self.mf_tool.get_scheme_historical_nav(scheme_code)
        if not raw_data:
            raise ValueError("No historical data available for the selected fund.")
        
        nav_data = pd.DataFrame(raw_data["data"])
        nav_data["date"] = pd.to_datetime(nav_data["date"], format="%d-%m-%Y")
        nav_data["nav"] = nav_data["nav"].astype(float)
        filtered_data = nav_data[
            (nav_data["date"] >= pd.to_datetime(start_date)) & 
            (nav_data["date"] <= pd.to_datetime(end_date))
        ]
        return filtered_data

    def calculate_changes(self, nav_data):
        nav_data["month"] = nav_data["date"].dt.to_period("M")
        monthly_nav = nav_data.groupby("month")["nav"].mean().reset_index()
        monthly_nav["percentage_change"] = monthly_nav["nav"].pct_change() * 100
        return monthly_nav

    def get_average_aum(self, year_quarter, as_json=True):
        all_funds_aum = []
        url = self.mf_tool._get_avg_aum  
        html = requests.post(url, headers=self.mf_tool._user_agent, data={"AUmType":'F', "Year_Quarter": year_quarter})
        soup = BeautifulSoup(html.text, 'html.parser')
        rows = soup.select("table tbody tr")
        for row in rows:
            aum_fund = {}
            if len(row.findAll('td')) > 1:
                aum_fund['Fund Name'] = row.select("td")[1].get_text().strip()
                aum_fund['AAUM Overseas'] = row.select("td")[2].get_text().strip()
                aum_fund['AAUM Domestic'] = row.select("td")[3].get_text().strip()
                all_funds_aum.append(aum_fund)

        if as_json:
            return pd.DataFrame(all_funds_aum).to_json(orient="records")
        else:
            return all_funds_aum