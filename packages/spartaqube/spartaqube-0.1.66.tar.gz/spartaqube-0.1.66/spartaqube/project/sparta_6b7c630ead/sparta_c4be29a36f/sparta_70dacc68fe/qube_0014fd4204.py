import json
from django.conf import settings as conf_settings


def sparta_7a3288947c(type='candlestick') ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    options = """{
        "showTicks": True,
        "renderTicks": {
            "showTicks": True,
            "divisions": 10,
        },
    }"""
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to plot a simple candlestick chart with lightweight chart',
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
  ohlcv=[apple_price_df['Open'], apple_price_df['High'], apple_price_df['Low'], apple_price_df['Close']], 
  title='Example candlestick',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with volumes', 'description':
        'Example to plot a simple candlestick chart with lightweight chart',
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
  ohlcv=[apple_price_df['Open'], apple_price_df['High'], apple_price_df['Low'], apple_price_df['Close'], apple_price_df['Volume']], 
  title='Example candlestick',
  height=500
)
plot_example"""
        }]


def sparta_a049a6ae10(type='line2') ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    options = """{
        "showTicks": True,
        "renderTicks": {
            "showTicks": True,
            "divisions": 10,
        },
    }"""
    return [{'title': f'{type.capitalize()}', 'description':
        f'Example to plot a simple {type} chart with lightweight chart',
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
  title='Example {type}',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} two lines', 'description':
        f'Example to plot multiple {type}s with lightweight chart',
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
  y=apple_price_df[['Close', 'Open']], 
  title='Example {type}',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} two lines stacked',
        'description':
        f'Example to plot multiple {type}s with lightweight chart',
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
  y=apple_price_df[['Close', 'Open']],
  stacked=True,
  title='Example {type}',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with time range', 'description':
        f'Example to plot a simple {type} chart with lightweight chart',
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
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""
        }]


def sparta_19c296e218() ->list:
    return sparta_a049a6ae10('line2')


def sparta_365862ed15() ->list:
    return sparta_a049a6ae10('bar2')


def sparta_163910df01() ->list:
    return sparta_a049a6ae10('area2')


def sparta_7b493b383c() ->list:
    return sparta_a049a6ae10('lollipop2')


def sparta_16cb32dce7() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    options_baseline_price = """{
    "baseline": [
      	{
          "defaultBaselinePrice": 200,
        },
    ]
    }"""
    type = 'ts_baseline'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to plot a simple baseline chart with lightweight chart',
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
  title='Example baseline',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom baseline',
        'description':
        'Example to plot a simple baseline chart with lightweight chart',
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
  title='Example baseline',
  options={options_baseline_price},
  height=500
)
plot_example"""
        }]


def sparta_041b1c07ba() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    options_shaded = """{
        "shadedBackground": {
            "lowColor": "rgb(50, 50, 255)",
            "highColor": "rgb(255, 50, 50)",
            "opacity": 0.8,
        },
    }"""
    type = 'ts_shaded'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to plot a simple shaded background chart with lightweight chart'
        , 'sub_description': '', 'code':
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
  shaded_background=apple_price_df['Close'], 
  title='Example',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom colors',
        'description':
        'Example to plot a simple shaded background chart with lightweight chart'
        , 'sub_description': '', 'code':
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
  shaded_background=apple_price_df['Close'], 
  title='Example',
  options={options_shaded},
  height=500
)
plot_example"""
        }]


def sparta_51824adacb() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    options = """{
        "showTicks": True,
        "renderTicks": {
            "showTicks": True,
            "divisions": 10,
        },
    }"""
    type = 'performance'
    return [{'title': f'{type.capitalize()}', 'description':
        f'Example to plot a simple {type} chart with lightweight chart',
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
  title='Example {type}',
  height=500
)
plot_example"""
        }]


def sparta_4c44a256b9() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    options_colors = """{
        "areaBands": {
            "fillColor": "#F5A623",
            "color": "rgb(19, 40, 153)",
            "lineColor": "rgb(208, 2, 27)",
            "lineWidth": 3,
            "custom_scale_axis": "Right",
        },
    }"""
    type = 'ts_area_bands'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to plot a simple shaded background chart with lightweight chart'
        , 'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=[apple_price_df['Close'], apple_price_df['High'], apple_price_df['Low']], 
  title='Example',
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom colors',
        'description':
        'Example to plot a simple shaded background chart with lightweight chart'
        , 'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=[apple_price_df['Close'], apple_price_df['High'], apple_price_df['Low']], 
  options={options_colors},
  height=500
)
plot_example"""
        }]

#END OF QUBE
