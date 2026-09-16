import yfinance as yf
ticker = yf.Ticker('MAPMYINDIA.NS')
info = ticker.info
print('Price:', info.get('currentPrice'))
print('P/E:', info.get('trailingPE'))
print('52W High:', info.get('fiftyTwoWeekHigh'))
print('52W Low:', info.get('fiftyTwoWeekLow'))
print('Profit Margin:', info.get('profitMargins'))
print('ROE:', info.get('returnOnEquity'))
print('Total Revenue:', info.get('totalRevenue'))
print('Net Income:', info.get('netIncomeToCommon'))
print('Revenue Growth:', info.get('revenueGrowth'))
print('Earnings Growth:', info.get('earningsGrowth'))
print('Debt to Equity:', info.get('debtToEquity'))
