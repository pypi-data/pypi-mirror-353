def sparta_7ad6fd2d08() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'STL'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='stl',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_ad14647749() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Wavelet'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='wavelet',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_a048093214() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'HMM'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='hmm',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_f64ba8a89f() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'CUSUM'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='cusum',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_e8f82e86fd() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Ruptures'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='ruptures',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_2b24b09299() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Z-score'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='zscore',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_d2536ed059() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Prophet Outlier'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='prophet_outlier',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_a4543134e1() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Isolation Forest'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='isolation_forest',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_3de17cdcb1() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'MAD'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='mad',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_5925fdf5c5() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'SARIMA'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='sarima',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_75008f93f2() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'ETS'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='ets',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_8182239958() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Prophet Forecast'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='prophet_forecast',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_2723340d8d() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'VAR'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
data_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='var',
  x=data_df.index,
  y=[data_df['Close'], data_df['Volume']],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_aad7f9d40d() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'ADF Test'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='adf_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_f4e9ad1f80() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'KPSS Test'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='kpss_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_8f81b788f8() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Perron Test'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='perron_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_7fc74fbb8c() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Zivot-Andrews Test'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='zivot_andrews_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_f6ad3b9e0d() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Granger Test'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker("^SPX").history(period="1y")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='granger_test',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_48fb2271b2() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Cointegration Test'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker("^SPX").history(period="1y")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='cointegration_test',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_62c844f609() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Canonical Correlation'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to run a simple linear regression', 'sub_description': '',
        'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
data_df = yf.Ticker("AAPL").history(period="1y")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='canonical_corr',
  x=[data_df['Close'], data_df['Open']],
  y=[data_df['High'], data_df['Volume']],
  title='Example',
  height=500
)
plot_example"""
        }]

#END OF QUBE
