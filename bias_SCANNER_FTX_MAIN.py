#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 12:02:50 2021

@author: ministudio
"""

import pandas as pd
from pandas.plotting import table
import matplotlib.pyplot as plt
import ccxt
import urllib.parse
import SCANNER_FTX_PERP as scanner
from alive_progress import alive_bar


def main(day= 1,month = 1,year = 2022):
    '''
    BACKTEST PARAMETERS
    '''
    # day = 10
    # month = 1 
    # year = 2022
    
    
    '''
    AUTHENTICATION
    '''
    print('\n(1) AUTHENTICATION')
    uri_nickname = urllib.parse.quote('Ciccio-test')
    ftx_client = ccxt.ftx({'apiKey': 'nbVpzQDHZ40dISTPRjhtPpOMPTeNCoF-eutKr9B5',
                           'secret': 'zqdRc9JyCJyTD-MdCZ-5QemnDkPyujgJO9MxGq-G',
                           'headers': {'FTX-SUBACCOUNT': uri_nickname}
                           })
    
    
    '''
    RETRIEVE ALL FUTURES FROM EXCHANGE
    '''
    print('\n(2) checking FUTURES on FTX.com ...')
    list_perp = scanner.get_all_futures(ftx_client)
    
    
    '''
    LAUNCH SCANNER
    '''     
    # TICKERS = ['tETHUSD','tXRPUSD']  
    results = {}
    file = open('report_FTX.txt', 'w')
    # [:10] per i test
    print(f'\n(3) STARTING SCANNER process from {day}-{month}-{year}: ')
    #with alive_bar(len(list_perp),length=20) as bar:
    for index, ticker in enumerate(list_perp, start=1):  
        results[ticker] = scanner.scanner(day,month,year,ticker,ftx_client)
        results[ticker][0].sort_values(by=['P/L %'], inplace=True, ascending=False)
        file = open('LOG/report_FTX.txt', 'a')
        log = f'\n{ticker}\t{results[ticker][0].iloc[0][0]}% ->\t{results[ticker][0].index[0]}'
        pct_value = round((index*100/len(list_perp)))
        print('\r...please wait... [%d%%]'%pct_value, end="")
        file.write('\n'+log)    
            #bar()
    
    
    '''
    DATA MINING
    '''
    print('\n(4) DATA MINING ...')
    best = pd.DataFrame(columns=['P_L','RANGE','VOLUME'])
    for ticker in results:
        best.loc[ticker] = [results[ticker][0].iloc[0][0], results[ticker][0].index[0], results[ticker][1]]
    
    
    # raggruppo in base al RANGE
    freq = best.groupby(['RANGE']).count()
    # mi prendo il valore in formato str dell'orario
    best_timeframe = freq.sort_values(by=['P_L'],ascending=False).iloc[0].name
    # passo il valore selezionando SOLO le coin di mio interesse
    best_coins = best.loc[best['RANGE'] == best_timeframe]
    best_coins.sort_values(by=['P_L'], inplace=True, ascending=False)
    # classifica in base al VOLUME rispetto al time range
    higher_time_vol = best_coins.sort_values(by=['VOLUME'], ascending=False)
    # classifica in base al solo VOLUME
    higher_vol = best.sort_values(by=['VOLUME'], ascending=False)
    
    try:
        print('SAVING files in "XLSX" Folder...')
        best_coins.to_excel('XLSX/best_coin_byTime.xlsx', sheet_name='best coin by time range')
        higher_time_vol.to_excel('XLSX/best_coin_byTime&Volume.xlsx', sheet_name='best coin by time & volume')
        higher_vol.to_excel('XLSX/best_coin_byVolume.xlsx', sheet_name='best coin by volume')
        print('...DONE !')
    
    except Exception as e:
        print(e)
    
    best.sort_values(by=['P_L'], inplace=True, ascending=False)
    print('\nTOP TEN by Profit/Loss')
    print(best.iloc[:10][:10])
    print('\nTOP TEN by ONLY VOLUME')
    print(higher_vol.iloc[:10][:10])
    print('\nTOP TEN by TIME RANGE')
    print(best_coins.iloc[:10][:10])
    print('\nTOP TEN by TIME RANGE -> VOLUME')
    print(higher_time_vol.iloc[:10][:10])
    
    
    '''
    PLOT FIGURE
    '''
    plt.figure(figsize=(16,8))
    
    # plot chart
    ax1 = plt.subplot(121, aspect='equal')
    freq.plot(kind='pie', 
              y = 'P_L', 
              ax=ax1, 
              autopct='%1.1f%%', 
              startangle=90, 
              shadow=False, 
              labels=freq.index, 
              legend = False, 
              fontsize=10)
    
    # # plot table
    # ax2 = plt.subplot(122)
    # plt.axis('off')
    # tbl = table(ax2, freq, loc='center')
    # tbl.auto_set_font_size(False)
    # tbl.set_fontsize(14)
    # plt.show()
    
    
if __name__ == '__main__':
    main()
