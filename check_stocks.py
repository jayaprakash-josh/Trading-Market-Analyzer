import yfinance as yf
tickers = ['CAMS.NS', 'HAL.NS', 'SONACOMS.NS']
for t in tickers:
    info = yf.Ticker(t).info
    print(f'\n--- {t} ---')
    print('Price:', info.get('currentPrice'))
    print('52W High:', info.get('fiftyTwoWeekHigh'))
    print('52W Low:', info.get('fiftyTwoWeekLow'))
    print('P/E:', info.get('trailingPE'))
    print('Profit Margin:', info.get('profitMargins'))
    print('Net Income:', info.get('netIncomeToCommon'))
    print('Revenue Growth:', info.get('revenueGrowth'))
    print('Earnings Growth:', info.get('earningsGrowth'))
    print('Debt/Equity:', info.get('debtToEquity'))
