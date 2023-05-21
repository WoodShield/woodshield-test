import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title("米国株価可視化アプリ")


#太字は*二つで囲む
# #とスペースで太字アンド改行
st.sidebar.write("""
# 米国株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")
#改行は\n

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.slider('日数',1,360,20)

st.write(f"""
### 過去{days}日間の米国株価
""")

#キャッシュに保存することでデータの読み込みを早くする（キャッシュを消す方法もある）
#@st.cache_data
def get_data(days,tickers):
  df = pd.DataFrame()
  for company in tickers.keys():
    tkr = yf.Ticker(tickers[company])
    hist = tkr.history(period=f"{days}d")
    hist.index = pd.to_datetime(hist.index).strftime('%d %B %Y')
    hist=hist[["Close"]]
    hist.columns=[company]
    hist=hist.T
    hist.index.name="Name"
    df = pd.concat([df,hist])
  return df


try: 
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 500.0, (0.0, 500.0)
    )

    tickers = {
        'apple': 'AAPL',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN',
        'palantir':'PLTR',
    }
    df = get_data(days, tickers)
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['google', 'amazon', 'apple','palantir','netflix','microsoft']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価 (USD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "なにかエラーが起きているようです。"
    )