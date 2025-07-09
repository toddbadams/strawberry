
from src.alpha_vantage.financial_data_injestor import FinancialDataInjestor
import os

def main():
    av_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    av_url =  os.getenv("ALPHA_VANTAGE_URL")
    data_path = os.getenv("OUTPUT_PATH", "data/")
    tickers = [
        "ABBV","CAH","NUE","PPG","SHW","ALB","CAT","GWW","ECL","SPGI",
        "AOS","EMR","KVUE","CINF","TGT","PNR","NDSN","APD","ESS","WMT",
        "EXPD","GD","LOW","DOV","ES","BEN","ADP","TROW","ROP","ITW",
        "FDS","CTAS","ABT","GPC","FAST","FRT","ATO","ED","LIN","MDT",
        "CVX","SWK","CHRW","CLX","CB","JNJ","ADM","BF-B","XOM","O",
        "MCD","NEE","MKC","IBM","KMB","KO","SJM","CL","PG","WST",
        "SYY","AFL","HRL","AMCR","PEP","BRO","CHD","ERIE","BDX"
    ]

    for ticker in tickers:
        print(f"extracting ticker: {ticker}")
        if not FinancialDataInjestor(av_api_key,data_path,ticker,av_url).extract():
            break

if __name__ == "__main__":
    main()
