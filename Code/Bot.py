import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pprint as pp
import csv

total_account_balance = 100000
risk_percentage = 0.1 

#Dateniniatlisierung 
def datainit(file,long,medium, short):
    rawdata=pd.read_csv(file)
    rawdata=rawdata.dropna()
    rawdata['SMALong']=SMA(rawdata,long)
    rawdata['SMAMed']=SMA(rawdata,medium)
    rawdata['SMAShort']=SMA(rawdata,short)
    cutdata=rawdata[rawdata['Date']>='2014-01-01']
    return cutdata

#Simple Moving Average Berechnung
def SMA(data,period:int,column='Close'):
    return data[column].rolling(window=period).mean()

#Generierung von Buy/Sell-Signalen und Speicherung der Daten in .csv files
def signals(data):
    global total_account_balance
    global risk_percentage
    buy = []
    sell = []
    profit = []
    open_positions = False
    share_amount=0
    trade_capital=total_account_balance*risk_percentage
    data['next_day_open']=data['Open'].shift(-1)
    stop_loss_percent=1
    stop_loss_price=0

    for index, row in data.iterrows():
        sma_short=row.loc['SMAShort']
        sma_med=row.loc['SMAMed']
        sma_long=row.loc['SMALong']
        close=row.loc['Close']
        trade_price=row.loc['next_day_open']
        if (sma_short>=sma_med and sma_short>sma_long and not open_positions):
            buy.append(close)
            sell.append(None)
            open_positions=True
            share_amount=trade_capital/trade_price
            stop_loss_price=trade_price*(1-stop_loss_percent)
        elif (open_positions and ((sma_short<=sma_med or sma_short<=sma_long) or close<=stop_loss_price)):
            sell.append(close)
            buy.append(None)
            open_positions=False
            total_account_balance=total_account_balance+(share_amount*trade_price-trade_capital)
            profit.append(share_amount*trade_price-trade_capital)
        else:
             buy.append(None)
             sell.append(None)
    data['Buy']=buy
    data['Sell']=sell
    with open('Ergebnisdaten/data_test.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SPY S'+ str(s)+'M'+str(m)+'L'+str(l)+ ' ' +str(stop_loss_percent)]) 
        for p in profit:
            writer.writerow([p])
    return(profit)

def statistics():
    profit=signals(data)
    np_profit=np.array(profit)
    result = {
        "Bester Trade": max(np_profit),
        "Schlechtester Trade": min(np_profit),
        "Durchschnittlicher Gewinn pro Trade": np.mean(np_profit),
        "Gewinn": sum(np_profit),
        "Einzelne Trades": []
    }
    for i in range(len(np_profit)):
        result["Einzelne Trades"].append({"Trade {}: ".format(i+1): np_profit[i]})
    r = pp.pp(result)
    return r

def printfigure(data):
    fig=go.Figure(data=[go.Candlestick(x=data.index,
                                   open=data['Open'],
                                   high=data['High'],
                                   low=data['Low'],
                                   close=data['Close'],name='Candles'),
                                    go.Scatter(x=data.index,y=data['SMAShort'],line=dict(color='blue',width=1),name='SMAShort'),
                                    go.Scatter(x=data.index,y=data['SMAMed'],line=dict(color='lime',width=1),name='SMAMed'),
                                    go.Scatter(x=data.index,y=data['SMALong'],line=dict(color='red',width=1),name='SMALong'),
                                    go.Scatter(x=data.index,y=data['Buy']+(data['Buy']*0.2),mode='markers',marker=dict(size=12.5, symbol='triangle-up',color='green'), name="Buy Signal"),
                                    go.Scatter(x=data.index,y=data['Sell']-(data['Sell']*0.2),mode='markers',marker=dict(size=12.5,symbol='triangle-down', color='crimson'), name="Sell Signal")
                                   ])
    fig.update_layout(paper_bgcolor='black',plot_bgcolor='black', margin_l=0, margin_r=0, margin_t=0, margin_b=0)
    fig.update_xaxes(color='white')
    fig.update_yaxes(color='white')
    fig.show()

l=200
m=50
s=20
data=datainit('Basisdaten/SPY10Y.csv',l,m,s)
data=data.set_index(pd.DatetimeIndex(data['Date'].values))
print(statistics())
printfigure(data)






