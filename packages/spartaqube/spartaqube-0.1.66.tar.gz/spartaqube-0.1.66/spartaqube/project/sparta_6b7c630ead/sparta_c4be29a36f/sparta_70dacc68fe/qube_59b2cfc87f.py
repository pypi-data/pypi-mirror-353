import json
from django.conf import settings as conf_settings


def sparta_8c3cb24da7() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'notebook'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a python Notebook', 'sub_description': '',
        'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  height=500
)
plot_example"""
        }]


def sparta_17556a8d6a() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    options_metrics = "{'reportType': 1}"
    options_plots = "{'reportType': 2}"
    options_dd = "{'reportType': 3}"
    type = 'quantstats'
    return [{'title': f'{type.capitalize()} basic report', 'description':
        'Example to display a quant report using QuantStats',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} metrics report', 'description':
        'Example to display a quant report using QuantStats',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  options={options_metrics},
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} plots report', 'description':
        'Example to display a quant report using QuantStats',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  options={options_plots},
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} drawdowns report', 'description':
        'Example to display a quant report using QuantStats',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  options={options_dd},
  height=500
)
plot_example"""
        }]


def sparta_7b2ac491ad() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'dataframe'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a quant report using QuantStats',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  dataframe=apple_price_df, 
  title='Example',
  height=500
)
plot_example"""
        }]


def sparta_30bbc0dea1() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'summary_statistics'
    return [{'title': f'{type.capitalize()}', 'description':
        'Summary Statistics Example', 'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  y=[apple_price_df['Close'], apple_price_df['Volume']], 
  title='Example',
  height=500
)
plot_example"""
        }]

#END OF QUBE
