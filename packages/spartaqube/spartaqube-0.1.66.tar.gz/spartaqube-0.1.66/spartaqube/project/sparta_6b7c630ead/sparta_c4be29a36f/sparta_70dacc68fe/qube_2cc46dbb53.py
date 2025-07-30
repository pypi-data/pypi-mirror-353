import json
from django.conf import settings as conf_settings


def sparta_cd1c7dbefa() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'dynamicRescale'
    return [{'title': f'{type.capitalize()}', 'description':
        'An interactive chart that resizes time series from any date, comparing performance metrics in real time'
        , 'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
msft = yf.Ticker('MSFT').history(period="24mo")[['Close']].rename(columns={{'Close': 'MSFT'}})
aapl = yf.Ticker('AAPL').history(period="24mo")[['Close']].rename(columns={{'Close': 'AAPL'}})
nvda = yf.Ticker('NVDA').history(period="24mo")[['Close']].rename(columns={{'Close': 'NVDA'}})
tsla = yf.Ticker('TSLA').history(period="24mo")[['Close']].rename(columns={{'Close': 'TSLA'}})

prices_df = msft
prices_df = prices_df.merge(aapl, left_index=True, right_index=True, how='inner')
prices_df = prices_df.merge(nvda, left_index=True, right_index=True, how='inner')
prices_df = prices_df.merge(tsla, left_index=True, right_index=True, how='inner')
prices_df.columns = ['MSFT', 'AAPL', 'NVDA', 'TSLA']
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  x=prices_df.index,
  y=prices_df,
  height=500
)
plot_example"""
        }]


def sparta_f4973b2c71() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'regression'
    return [{'title': f'{type.capitalize()}', 'description':
        'Regression Plot: Analyzing Trends and Relationships in Data',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
msft = yf.Ticker('MSFT').history(period="24mo")[['Close']].rename(columns={{'Close': 'MSFT'}})
msft_returns = msft.pct_change()
aapl = yf.Ticker('AAPL').history(period="24mo")[['Close']].rename(columns={{'Close': 'AAPL'}})
aapl_returns = aapl.pct_change()
prices_df = msft
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  x=aapl_returns,
  y=msft_returns,
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_ab1cbefda4() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'calendar'
    return [{'title': f'{type.capitalize()}', 'description':
        'Weekday Calendar Heatmap: Mapping Daily Values Across Weeks and Days',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
msft = yf.Ticker('MSFT').history(period="24mo")[['Close']].rename(columns={{'Close': 'MSFT'}})
prices_df = msft
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  x=prices_df.index,
  y=prices_df,
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_f090a7e0a8() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'wordcloud'
    return [{'title': f'{type.capitalize()}', 'description':
        'Word Cloud: Visualizing Text Data Frequency and Importance',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
wordcloud = ['crypto', 'crypto', 'crypto', 'btc', 'btc', 'eth', 'satoshi', 'sol', 'tech', 'ia', 'ia', 'GPT']
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=wordcloud,
  interactive=False,
  height=500
)
plot_example"""
        }]

#END OF QUBE
