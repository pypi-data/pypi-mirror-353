def sparta_511f5ad3ee() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'OLS'
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
  chart_type='OLS',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_59f71ec7f7() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Polynomial Regression'
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
  chart_type='PolynomialRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_c3797f799c() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Decision Tree Regression'
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
  chart_type='DecisionTreeRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_0ba8de97bc() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Random Forest Regression'
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
  chart_type='RandomForestRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_161810e586() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Clustering'
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
  chart_type='clustering',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_7cb6d71f04() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Correlation Network'
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
  chart_type='correlation_network',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_25981d1370() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'PCA'
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
  chart_type='pca',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_156d032dae() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'TSNE'
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
  chart_type='tsne',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_3a4a8cac14() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Features importance'
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
  chart_type='features_importance',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_d7e30eaf8c() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Mutual Information'
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
  chart_type='mutual_information',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_58804447ed() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Quantile Regression'
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
  chart_type='quantile_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_ee4ee113cb() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Rolling Regression'
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
  chart_type='rolling_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_dadf2d66f1() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'Recursive Regression'
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
  chart_type='recursive_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""
        }]

#END OF QUBE
