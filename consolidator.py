
from src.consolidators.data_consolidator import DataConsolidator
import os

def main():
    data_path = os.getenv("OUTPUT_PATH", "data/")
    tickers = [
        "ABBV"  # ,"CAH","NUE","PPG","SHW","ALB","CAT","GWW","ECL","SPGI"
        
    ]

    for ticker in tickers:
        print(f"consolidating ticker: {ticker}")
        DataConsolidator(data_path).consolidate(ticker)

if __name__ == "__main__":
    main()


""" 
        ,
        "AOS","EMR","KVUE","CINF","TGT","PNR","NDSN","APD","ESS","WMT",
        "EXPD","GD","LOW","DOV","ES","BEN","ADP","TROW","ROP","ITW",
        "FDS","CTAS","ABT","GPC","FAST","FRT","ATO","ED","LIN","MDT",
        "CVX","SWK","CHRW","CLX","CB","JNJ","ADM","BF-B","XOM","O",
        "MCD","NEE","MKC","IBM","KMB","KO","SJM","CL","PG","WST",
        "SYY","AFL","HRL","AMCR","PEP","BRO","CHD","ERIE","BDX"
        """