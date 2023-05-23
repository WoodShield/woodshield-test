import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title("米国株価可視化アプリ")

st.sidebar.write("""
# 米国株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.number_input('日数',min_value=0, max_value=int(1e9), value=20)

st.write(f"""
### 過去{days}日間の米国株価
""")

def get_data(days,tickers):
  df = pd.DataFrame()
  for ticker in tickers:
    tkr = yf.Ticker(ticker)
    hist = tkr.history(period=f"{days}d")
    hist.index = pd.to_datetime(hist.index).strftime('%d %B %Y')
    hist=hist[["Close"]]
    hist.columns=[ticker]
    hist=hist.T
    hist.index.name="Name"
    df = pd.concat([df,hist])
  return df

try: 
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin = st.sidebar.number_input('最小値を入力してください。', min_value=0, max_value=int(1e9), value=0)
    ymax = st.sidebar.number_input('最大値を入力してください。', min_value=0, max_value=int(1e9), value=300)

    # tickersリストをテキスト入力から生成
    tickers_text = st.sidebar.text_input("ティッカーをカンマで区切って入力してください：", 'AAPL,GOOGL,MSFT,NFLX,AMZN,PLTR')
    tickers = [s.strip() for s in tickers_text.split(",")]

    df = get_data(days, tickers)

    # デフォルトの選択項目をtickersリストに基づいて動的に更新
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        tickers
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
