import time
import pyupbit
import datetime
import numpy as np
import requests
import os
import pause

access = "UyGaDoA6B0feAB4szUVp4Dwhs648ouRyxJV4hOjQ"
secret = "4pAT7IzkxI4GqTmSnKbosdarnwD1QJSamakQUCLO"
myToken = "xoxb-1831041840644-1991574409638-HRIpOqdpYiysHSNW823T5yx4"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

import pyupbit
import numpy as np



k= 0.3
coin_name = "KRW-BTT"

# 로그인
upbit = pyupbit.Upbit(access, secret)
# 시작 메세지 슬랙 전송
post_message(myToken,"#coin", f"{coin_name} Autotrade start")
print(f"{coin_name} Autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(coin_name)
        end_time = start_time + datetime.timedelta(days=1)
        today = datetime.date
        # print('{0} 자동 매매를 시작합니다.'.format(today))

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(coin_name, k)
            h_target_price = round(target_price * 1.3,2)
            l_target_price = round(target_price * 1.002, 2)
            current_price = get_current_price(coin_name)
            if target_price < current_price :
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order(coin_name, krw*0.9995)
                    post_message(myToken,"#coin", f"{coin_name} buy : " +str(buy_result))
                    # time.sleep(3)
                    coin = get_balance(coin_name)
                    if h_target_price <= current_price :
                        sell_result = upbit.sell_market_order(coin_name, coin)
                        post_message(myToken, "#coin", f"[High price sell] {coin_name} sell : " + str(sell_result))
                        pause.until(end_time - datetime.timedelta(seconds=10))
                        print("#coin", "20% 초과 목표 매도가 발생하여, {0} 매매를 중단합니다.".format(today))
                        post_message(myToken, "#coin", "20% 초과 목표 매도가 발생하여, {0} 매매를 중단합니다.".format(today))
                    # elif l_target_price == current_price :
                    #     sell_result = upbit.sell_market_order(coin_name, coin * 0.9995)
                    #     post_message(myToken, "#coin", f"[Low price sell] {coin_name} sell : " + str(sell_result))
        else:
            coin = get_balance(coin_name)
            if coin > 0:
                sell_result = upbit.sell_market_order(coin_name, coin)
                post_message(myToken,"#coin", f"[close time sell] {coin_name} sell : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#coin", e)
        time.sleep(1)
