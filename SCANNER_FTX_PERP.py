#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 12:02:50 2021

@author: ministudio
"""

from datetime import datetime, timezone
import pandas as pd
import numpy as np
from alive_progress import alive_bar


def get_all_futures(ftx_client):
    tickers = ftx_client.fetchMarkets()
    list_perp =[]
    
    #with alive_bar(len(tickers),length=20) as bar:
    for ticker in tickers:
        if 'PERP' in ticker['id']: 
            list_perp.append(ticker['id'])
            #bar()

    return list_perp


def scanner(day,month,year,ticker,ftx): 
    results = pd.DataFrame(columns=['P/L %'])
    start_trade = datetime(year, month, day, 0, 0, 0)
    timestamp = start_trade.replace(tzinfo=timezone.utc).timestamp()
    candles = ftx.fetchOHLCV(ticker, timeframe='1h', since=timestamp*1000, limit=5000)
    candles_df = pd.DataFrame(candles, columns=['MTS','OPEN','HIGH','LOW','CLOSE','VOLUME'])
    volume = candles_df.VOLUME.sum()
    
    for j in range(0,24):
        # algoritmo per andare di candela in candela
        ledger = pd.DataFrame(columns=['POSITION','ENTRY PRICE','P_L SINGLE','P_L TOTAL'])
        long = True
        time_scanner = ''
        
        # calcolo l'offset tra una candela e l'altra di mio interesse 
        offset = 12
        
        if j != 0:
            candles = candles[1:] 
        
        try:
            for i in range(0,len(candles),offset):
                entry_price = candles[i][1]
                    
                if i == 0:
                    start = datetime.utcfromtimestamp(candles[i][0]/1000)
                    end = datetime.utcfromtimestamp(candles[i+offset][0]/1000) #datetime.utcfromtimestamp(candles[i+offset+10][0]/1000)
                    #print('FROM',start.strftime("%H:%M"),'TO',end.strftime("%H:%M"))
                    var_pct = p_l_total = 0
                    position = 'LONG'
                    time_scanner = f'{start.strftime("%H:%M")} to {end.strftime("%H:%M")}'
                    
                else:
                    #r_exit_entry = candles[i][4]/candles[i-offset][4] #if not long else candles[i][4]/candles[i-offset][4]
                    
                    # calcolo il profitto
                    if long:
                        var_pct = round((candles[i-offset][1] - candles[i][1])/candles[i-offset][1]*100, 3)
                        p_l_total = ledger['P_L TOTAL'].iloc[-1] + var_pct
                    
                    if not long:
                        var_pct = round((candles[i][1]-candles[i-offset][1])/candles[i][1]*100, 3)
                        p_l_total = ledger['P_L TOTAL'].iloc[-1] + var_pct
              
                if long:
                    date = datetime.utcfromtimestamp(candles[i][0]/1000)
                    position = 'LONG'
                    long = False
                else:
                    # quindi vado in short
                    date = datetime.utcfromtimestamp(candles[i][0]/1000) #candles[i+10][0]/1000
                    position = 'SHORT'
                    long = True
            
                ledger.loc[date] = [position, entry_price, var_pct, p_l_total]
                  
            results.loc[time_scanner] =  round(ledger['P_L TOTAL'][-1],2)
            #print('P/L  TOTAL  :\t',round(ledger['P_L TOTAL'][-1],2), '%\n') 
            
        except Exception as e: 
            results.loc[time_scanner] =  np.NAN
        
    return results, volume

