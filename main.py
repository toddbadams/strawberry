from src.merge_quarterly_financials import merge_quarterly_financials
from src.data_ingress.fetch_alpha_vantage_data import AlphaVantageDataIngress
import pandas as pd
import os

def main(symbol="UPS"):
    
    # get the API key from environment variable
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is not set.")
    
    # get the url for apha vantage data
    url =  os.getenv("ALPHA_VANTAGE_URL")
    if not url:
        raise ValueError("ALPHA_VANTAGE_URL environment variable is not set.")  
    
    # get the output path from environment variable
    output_path = os.getenv("OUTPUT_PATH", "data/")
    if not output_path:
        raise ValueError("OUTPUT_PATH environment variable is not set.")
    
    # creaete the AlphaVantageData object
    a = AlphaVantageDataIngress(api_key, url, symbol, output_path)

  #  merge_quarterly_financials(
  #      "data/UPS_quarterly_balance_sheet_data.csv",
  #      "data/UPS_quarterly_cash_flow_data.csv",
  #      "data/UPS_quarterly_adjusted_time_series_data.csv",
  #      "data/UPS_quarterly_income_statement_data.csv",
  #      "data/UPS_quarterly_merged_data.csv"
  #  )
    
    bs = a.read_balance_sheets()
    cf = a.read_cash_flow_statements()
    ap = a.read_monthly_adjusted_time_series()
    is_ = a.read_income_statements()

    merge_quarterly_financials(bs,cf,ap,is_)

if __name__ == "__main__":
    main()
